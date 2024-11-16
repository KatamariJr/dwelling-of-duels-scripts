package main

import (
	"dodSubmissionsHelper/internal/server"
	"log"
)

func main() {
	port := 4000
	srv := server.New(port)
	log.Printf("listening at %d\n", port)
	log.Fatal(srv.ListenAndServe())
}
