utf-8-test.codepoints.txt: UTF-8-demo.txt bin/codepoints.pl
	bin/codepoints.pl "$<" >"$@.tmp"
	mv "$@.tmp" "$@"

UTF-8-demo.txt: FORCE
	curl -s "https://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-demo.txt" >"$@.tmp"
	mv "$@.tmp" "$@"

.PHONY: FORCE
