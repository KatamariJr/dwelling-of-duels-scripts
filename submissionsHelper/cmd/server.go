package main

import (
	"dodSubmissionsHelper/internal/server"
	"fmt"
	"log"
	"os/exec"
	"runtime"
)

func main() {
	port := 4000
	srv := server.New(port)
	log.Printf("listening at %d\n", port)
	browserErr := openbrowser(fmt.Sprintf("http://localhost:%d", port))
	if browserErr != nil {
		log.Printf("Attempted to helpfully open browser but failed: %s\n", browserErr)
	}
	log.Fatal(srv.ListenAndServe())
}

func openbrowser(url string) error {
	var err error
	switch runtime.GOOS {
	case "linux":
		err = exec.Command("xdg-open", url).Start()
	case "windows":
		err = exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	case "darwin":
		err = exec.Command("open", url).Start()
	default:
		err = fmt.Errorf("unsupported platform")
	}
	return err
}
