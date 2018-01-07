FILES= Tokenizer.py Main.py JackCompiler CompilationEngine.py SymbolTable.py VMWriter.py

all:
	chmod a+x JackCompiler


ttest: Tokenizer.py tokentest.py
	python tokentest.py something.jack

git: 
	git add $(FILES) README Makefile
	git commit -m"from makefile"
	git push

clean:
	rm *.pyc

tar: $(FILES)
	tar -cvf Project11 README Makefile $(FILES)
