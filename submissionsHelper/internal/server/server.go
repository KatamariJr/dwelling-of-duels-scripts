package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/davecgh/go-spew/spew"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/samber/lo"
	lop "github.com/samber/lo/parallel"
	"log"
	"net/http"
	"os/exec"
	"path"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

type Server struct {
	*http.Server
	*session.Session
	*s3.S3
}

type problem struct {
	Id   string `json:"id"`
	Kind string `json:"kind"`
}

type fetchResult struct {
	Data        []songData `json:"data"`
	Problems    []problem  `json:"problems"`
	DeletedData []songData `json:"deletedData"`
}

type songData struct {
	SubmissionTime time.Time `json:"submissionTime"`
	SongTitle      string    `json:"songTitle"`
	ArtistNames    string    `json:"artistNames"`
	GameNames      string    `json:"gameNames"`
	Comments       string    `json:"comments"`
	SubmitterEmail string    `json:"submitterEmail"`
	IsAlt          bool      `json:"isAlt,string"`
	Filename       string    `json:"filename"`
	Lyrics         string    `json:"lyrics"`
	Score          float64   `json:"score"`
	Identity       struct {
		UserAgent string `json:"userAgent"`
		SourceIP  string `json:"sourceIP"`
		Caller    string `json:"caller"`
	} `json:"identity"`
	UUID string `json:"uuid"`
}

type voteData struct {
	SubmissionTime time.Time `json:"submissionTime"`
	SubmitterEmail string    `json:"submitterEmail"`
	Votes          string    `json:"votes"`
	Score          float64   `json:"score"`
	Identity       struct {
		UserAgent string `json:"userAgent"`
		SourceIP  string `json:"sourceIP"`
		Caller    string `json:"caller"`
	} `json:"identity"`
	UUID string `json:"uuid"`
}

const bucketName = "dwellingofduels-static-site"
const uploadKeyPrefix = "upload-form/"
const deletedKeyPrefix = "upload-form/deleted/"
const votingKeyPrefix = "voting-form/"

func (s *Server) healthCheck() http.HandlerFunc {
	type response struct {
		Ready bool `json:"ready"`
	}
	return func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(200)
		err := json.NewEncoder(w).Encode(response{Ready: true})
		if err != nil {
			log.Println(err)
		}
	}
}

func splitJsonAndMp3(files []*s3.Object) (jsonFiles, mp3Files []*s3.Object) {
	//filter original down to just json
	jsonFiles = lo.Filter(files, func(item *s3.Object, index int) bool {
		return strings.Contains(*item.Key, ".json")
	})

	mp3Files = lo.Filter(files, func(item *s3.Object, index int) bool {
		return strings.Contains(*item.Key, ".mp3")
	})
	return jsonFiles, mp3Files
}

func (s *Server) fetchSubmissionsHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		output, err := s.S3.ListObjectsV2(&s3.ListObjectsV2Input{
			Bucket: aws.String(bucketName),
			Prefix: aws.String(uploadKeyPrefix),
		})
		if err != nil {
			w.WriteHeader(500)
			log.Println("[ERR] listing objects", err)
			return
		}

		deletedFiles := lo.Filter(output.Contents, func(item *s3.Object, index int) bool {
			return strings.Contains(*item.Key, "deleted")
		})
		nonDeletedFiles := lo.Filter(output.Contents, func(item *s3.Object, index int) bool {
			return !strings.Contains(*item.Key, "deleted")
		})

		deletedJsonFiles, _ := splitJsonAndMp3(deletedFiles)
		nonDeletedJsonFiles, nonDeletedMp3Files := splitJsonAndMp3(nonDeletedFiles)

		//check if any json files dont have matching MP3
		problems := []problem{}
	outerLoop:
		for _, v := range nonDeletedJsonFiles {
			jsonUuid := strings.Split(path.Base(*v.Key), ".")[0]
			for _, w := range nonDeletedMp3Files {
				mp3Uuid := strings.Split(path.Base(*w.Key), ".")[0]
				if mp3Uuid == jsonUuid {
					continue outerLoop
				}
			}
			problems = append(problems, problem{Id: jsonUuid, Kind: "orphaned song data"})
		}

		spew.Println("count:", len(problems))
		spew.Println("problems:", problems)

		log.Printf("fetching %v objects\n", len(nonDeletedJsonFiles))

		//read the contents of the files
		nonDeletedSongData, nonDeletedDownloadBytes := s.fetchAndReadJsonFiles(nonDeletedJsonFiles)
		deletedSongData, deletedDownloadBytes := s.fetchAndReadJsonFiles(deletedJsonFiles)

		log.Println("Total downloaded bytes", nonDeletedDownloadBytes+deletedDownloadBytes)

		returnData := fetchResult{Data: nonDeletedSongData, Problems: problems, DeletedData: deletedSongData}

		jsonBytes, err := json.Marshal(returnData)
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] marshaling song data: %v\n", err)
			return
		}

		w.Header().Add("Content-Type", "application/json")
		w.Write(jsonBytes)
	}
}

func (s *Server) fetchAndReadJsonFiles(jsonFiles []*s3.Object) ([]songData, int64) {
	allSongFileData := []songData{}
	allSongFileDataLock := sync.Mutex{}
	var totalDownloadedBytes int64 = 0
	lop.ForEach(jsonFiles, func(item *s3.Object, index int) {
		res, err := s.S3.GetObject(&s3.GetObjectInput{
			Bucket: aws.String(bucketName),
			Key:    item.Key,
		})
		if err != nil {
			log.Println("[ERR] getting obj data", err)
			return
		}

		atomic.AddInt64(&totalDownloadedBytes, *res.ContentLength)

		data := songData{}
		err = json.NewDecoder(res.Body).Decode(&data)
		if err != nil {
			log.Printf("decoding song data for %p: %v\n", item.Key, err)
			return
		}

		data.UUID = strings.TrimSuffix(path.Base(*item.Key), ".json")

		allSongFileDataLock.Lock()
		allSongFileData = append(allSongFileData, data)
		allSongFileDataLock.Unlock()
	})

	//sort it in a predictable order
	sort.Slice(allSongFileData, func(i, j int) bool {
		return allSongFileData[i].SubmissionTime.Before(allSongFileData[j].SubmissionTime)
	})

	return allSongFileData, totalDownloadedBytes
}

func (s *Server) editSubmissionsHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		//decode input
		var input = &songData{}
		err := json.NewDecoder(r.Body).Decode(&input)
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] decoding input data: %v\n", err)
			return
		}

		marshaled, err := json.Marshal(input)
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] marshaling input data: %v\n", err)
			return
		}

		jsonBuffer := bytes.Buffer{}
		err = json.Indent(&jsonBuffer, marshaled, "", "\t")
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] indenting output json: %v\n", err)
			return
		}

		theKey := fmt.Sprintf("%s%s.json", uploadKeyPrefix, input.UUID)
		_, err = s.S3.PutObject(&s3.PutObjectInput{
			Bucket: aws.String(bucketName),
			Key:    aws.String(theKey),
			Body:   bytes.NewReader(jsonBuffer.Bytes()),
		})
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] indenting output json: %v\n", err)
			return
		}

		log.Println("update success")

		w.WriteHeader(200)
	}
}

func (s *Server) undeleteSubmissionHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// get the uuid from the request url
		uuid, ok := mux.Vars(r)["uuid"]
		if !ok {
			w.WriteHeader(http.StatusUnprocessableEntity)
			w.Write([]byte("incorrect uuid given"))
			return
		}

		err := s.moveSongData(deletedKeyPrefix, uuid, uploadKeyPrefix)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			log.Println(err)
			return
		}

	}
}

func (s *Server) deleteSubmissionHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// get the uuid from the request url
		uuid, ok := mux.Vars(r)["uuid"]
		if !ok {
			w.WriteHeader(http.StatusUnprocessableEntity)
			w.Write([]byte("incorrect uuid given"))
			return
		}

		err := s.moveSongData(uploadKeyPrefix, uuid, deletedKeyPrefix)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			log.Println(err)
			return
		}

	}
}

// moveSongData will move mp3 and json data to the destinationFolder. sourceFolder and destinationFolder should have a trailing slash.
func (s *Server) moveSongData(sourceFolder string, uuid string, destinationFolder string) error {
	originalMp3FileKey := fmt.Sprintf("%s%s.mp3", sourceFolder, uuid)
	originalJsonFileKey := fmt.Sprintf("%s%s.json", sourceFolder, uuid)

	//copy the mp3 file
	_, err := s.S3.CopyObject(&s3.CopyObjectInput{
		Key:        aws.String(fmt.Sprintf("%s%s.mp3", destinationFolder, uuid)),
		Bucket:     aws.String(bucketName),
		CopySource: aws.String(fmt.Sprintf("%s/%s", bucketName, originalMp3FileKey)),
	})
	if err != nil {
		return fmt.Errorf("error copying mp3: %w", err)
	}

	//copy the json file
	_, err = s.S3.CopyObject(&s3.CopyObjectInput{
		Key:        aws.String(fmt.Sprintf("%s%s.json", destinationFolder, uuid)),
		Bucket:     aws.String(bucketName),
		CopySource: aws.String(fmt.Sprintf("%s/%s", bucketName, originalJsonFileKey)),
	})
	if err != nil {
		return fmt.Errorf("error copying json: %w", err)
	}

	//delete the files
	_, err = s.S3.DeleteObjects(&s3.DeleteObjectsInput{
		Bucket: aws.String(bucketName),
		Delete: &s3.Delete{
			Objects: []*s3.ObjectIdentifier{
				{
					Key: aws.String(originalMp3FileKey),
				},
				{
					Key: aws.String(originalJsonFileKey),
				},
			},
		},
	})
	if err != nil {
		return fmt.Errorf("error deleting files: %w", err)
	}

	return nil
}

func (s *Server) fetchVotingHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		output, err := s.S3.ListObjectsV2(&s3.ListObjectsV2Input{
			Bucket: aws.String(bucketName),
			Prefix: aws.String(votingKeyPrefix),
		})
		if err != nil {
			w.WriteHeader(500)
			log.Println("[ERR] listing objects", err)
			return
		}

		voteFiles := output.Contents

		log.Printf("fetching %v objects\n", len(voteFiles))

		//read the contents of the files
		allVoteFileData := []voteData{}
		allVoteFileDataLock := sync.Mutex{}
		var totalDownloadedBytes int64 = 0
		lop.ForEach(voteFiles, func(item *s3.Object, index int) {
			res, err := s.S3.GetObject(&s3.GetObjectInput{
				Bucket: aws.String(bucketName),
				Key:    item.Key,
			})
			if err != nil {
				w.WriteHeader(500)
				log.Println("[ERR] getting obj data", err)
				return
			}

			atomic.AddInt64(&totalDownloadedBytes, *res.ContentLength)

			data := voteData{}
			err = json.NewDecoder(res.Body).Decode(&data)
			if err != nil {
				w.WriteHeader(500)
				log.Printf("[ERR] decoding song data for %p: %v\n", item.Key, err)
				return
			}

			data.UUID = path.Base(*item.Key)

			allVoteFileDataLock.Lock()
			allVoteFileData = append(allVoteFileData, data)
			allVoteFileDataLock.Unlock()
		})
		log.Println("Total downloaded bytes", totalDownloadedBytes)

		//sort it in a predictable order
		sort.Slice(allVoteFileData, func(i, j int) bool {
			return allVoteFileData[i].SubmissionTime.Before(allVoteFileData[j].SubmissionTime)
		})

		jsonBytes, err := json.Marshal(allVoteFileData)
		if err != nil {
			w.WriteHeader(500)
			log.Printf("[ERR] marshaling song data: %v\n", err)
			return
		}

		w.Header().Add("Content-Type", "application/json")
		w.Write(jsonBytes)
	}
}

func New(port int) *Server {
	if port == 0 {
		panic("port is not set")
	}
	httpServer := &http.Server{
		Addr: fmt.Sprintf("127.0.0.1:%d", port),
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 30 * time.Second,
		ReadTimeout:  30 * time.Second,
	}

	log.Printf("Bucket: %s\n", bucketName)

	srv := &Server{}

	r := mux.NewRouter()
	r.Use(mux.CORSMethodMiddleware(r), Middleware)
	r.HandleFunc("/fetchVoting", srv.fetchVotingHandler())
	r.HandleFunc("/fetch", srv.fetchSubmissionsHandler())
	r.HandleFunc("/save", srv.editSubmissionsHandler())
	r.HandleFunc("/ready", srv.healthCheck()).Methods("GET", "OPTIONS")
	r.HandleFunc("/delete/{uuid}", srv.deleteSubmissionHandler()).Methods("DELETE")
	r.HandleFunc("/undelete/{uuid}", srv.undeleteSubmissionHandler()).Methods("POST")
	r.HandleFunc("/votes", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "./static/votes/index.html")
	})
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "./static/index.html")
	})
	r.HandleFunc("/script.js", func(w http.ResponseWriter, r *http.Request) {
		log.Println("compiling typescript")
		err := exec.Command("tsc").Run()
		if err != nil {
			log.Println(err)
		}
		http.ServeFile(w, r, "./static/script.js")
	})
	r.HandleFunc("/script.js.map", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "./static/script.js.map")
	})
	r.HandleFunc("/style.css", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "./static/style.css")
	})

	httpServer.Handler = handlers.CORS(handlers.AllowedOrigins([]string{"*"}))(r)

	srv.Server = httpServer

	srv.Session = session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	srv.S3 = s3.New(srv.Session, aws.NewConfig().WithRegion("us-east-1"))

	return srv
}

func Middleware(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("Start [%v] %v%v\n", r.Method, r.Host, r.URL.Path)
		// do stuff before the handlers
		h.ServeHTTP(w, r)
		// do stuff after the handlers
		log.Printf("End [%v] %v%v - duration %vms\n", r.Method, r.Host, r.URL.Path, time.Since(start).Milliseconds())
	})
}
