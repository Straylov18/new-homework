
зависимости под убунту
```shell
sudo apt install pandoc
sudo apt install texlive-xetex
sudo apt-get install texlive-lang-all
```
конвертация
```shell
pandoc README.md --pdf-engine=xelatex \
      -V mainfont="Lato-Medium" \
      -V geometry="margin=3cm" \
      -V lang="ru" \
      -o Manual.pdf
```