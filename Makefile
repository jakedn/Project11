FILES= Tokinizer.py Main.py JackAnalyzer CompilationEngine.py

all:
	chmod a+x JackAnalyzer


ttest: Tokenizer.py tokentest.py
	python tokentest.py something.jack

clean:
	rm *.pyc

tar: $(FILES)
	tar -cvf Project10 README Makefile $(FILES)
