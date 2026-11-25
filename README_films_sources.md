# Источники каталога films.json

В `films.json` находится 51 запись: 38 международных фильмов и 13 фильмов/кинопродукций Казахстана. Поле `source` добавлено к каждой записи как дополнительное поле для проверки происхождения метаданных.

## Международные фильмы и две международные копродукции с Казахстаном

Год, длительность, жанры, страны производства и языки взяты из файла `films_big.json`, ранее собранного из `tmdb_5000_movies.csv` (TMDb 5000 Movies Dataset). Для каждой записи сохранена индивидуальная страница фильма TMDb в поле `source` (`https://www.themoviedb.org/movie/ID`). Значения в каталоге нормализованы на русский язык: например, `Drama` → `драма`, `United States` → `США`, `Kazakhstan` → `Казахстан`.

## Казахстанские фильмы

Год, продолжительность, страны производства и языки проверяются по источникам, указанным в поле `source` каждой записи. Для части каталога использованы также карточки библиотеки UCL и фестивальные каталоги:

- [UCL — Central Asian feature films](https://www.ucl.ac.uk/library/using-library/libraries-and-study-spaces/ssees-library/bain-graffy-film-collection/central-asian-feature-films): `Уроки гармонии`, `Раненый ангел`, `Земля отцов` и другие записи из казахстанского раздела; источник содержит год, длительность и языки.
- [IFFR — A Dark, Dark Man](https://iffr.com/en/iffr/2020/films/a-dark-dark-man): год, 130 минут, Казахстан и Франция, казахский и русский языки.
- [Официальная страница фильма — The Gentle Indifference of the World](https://adilkhanyerzhanov.com/en/films/the-gentle-indifference-of-the-world/): год, 100 минут, страны производства.
- [Официальная страница фильма — The Owners](https://adilkhanyerzhanov.com/en/films/the-owners/): год, 93 минуты, Казахстан.
- [Каталог кинофестиваля Eurasia — Farewell, Gulsary! (PDF)](https://www.uni-passau.de/fileadmin/dokumente/projekte/centralasiaascinematicterritory/catalogues/EURASIA_IFF_2008.pdf): год, 102 минуты, Казахстан, казахский язык.
- [Каталог Doha Tribeca Film Festival — Myn Bala (PDF)](https://media.dohafilm.com/sites/default/files/prod/2025-05/DTFF2012Catalogue-EN.pdf): год, 108 минут, Казахстан, казахский язык.
- [IFFR — Schizo](https://iffr.com/en/iffr/2005/films/schizo): год, 86 минут, страны производства, русский язык.
- [Казахфильм — Баксы](https://kazakhfilm.kz/baksy): год, страны/язык и сюжет; длительность сверена с UCL.
- [IFFR — Aksuat](https://iffr.com/en/iffr/2000/films/aksuat): год, 78 минут, Япония и Казахстан, казахский язык.

`title` и `description` оформлены по-русски; краткие описания являются редакционными синопсисами и не используются как источник для года, длительности, стран или языков.
