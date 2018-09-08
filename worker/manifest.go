package main

type Manifest struct {
	Environment  map[string]interface{}
	Image        string
	Packages     []string
	Repositories map[string]string
	Secrets      []string
	Sources      []string
	Tasks        []map[string]string
}
