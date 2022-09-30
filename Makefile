all: website cv

website: cv
	PYTHONPATH=. pipenv run python ./generate.py

cv:
	mkdir -p /tmp/Website-latexmk-tmpdir
	latexmk -pdf -cd -output-directory=/tmp/Website-latexmk-tmpdir src/millard_cv.tex
	cp /tmp/Website-latexmk-tmpdir/millard_cv.pdf src/assets/millard_cv.pdf
