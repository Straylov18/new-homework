
зависимости под убунту
```shell
sudo apt install pandoc
sudo apt install texlive-xetex
sudo apt-get install texlive-lang-all
```
конвертация
```shell
pandoc README.md --pdf-engine=xelatex -o Manual.pdf
```