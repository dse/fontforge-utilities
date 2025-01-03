default:
	@echo make wgl4.txt

wgl4.txt: FORCE
	curl -s "https://www.cl.cam.ac.uk/~mgk25/ucs/wgl4.txt" >"$@.tmp"
	mv "$@.tmp" "$@"

.PHONY: FORCE
