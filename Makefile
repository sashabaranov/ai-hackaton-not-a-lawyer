.PHONY: scrape

scrape: scrape.py
	mkdir data | true
	python scrape.py

build_index: build_index.py
	rm -rf chroma.db | true
	python build_index.py
