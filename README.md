# nobo
![](https://img.shields.io/badge/Ritsumeikan%20University-API-blue.svg?colorA=990000&colorB=444444&longCache=true&style=flat) ![](https://img.shields.io/badge/Python-3.7.1-green.svg?longCache=true&style=flat) ![](https://img.shields.io/badge/Chrome-WebDriver-blue.svg?logo=Google%20Chrome&style=flat)

"nobo" means "No Borders", also means "登る" in Japanese.

**nobo** is a spider that you could get your data from each service provides by Ritsumeikan Univ.

You can use **nobo** to build your API with many frameworks (`Flask`, `Django` etc.) under GPLv3 License.

# NOTICE:
Ritsumeikan University deployed f5 obfuscator several months ago. :(  
Although, I don't know the situation in other schools. The truth is legacy version cannot work perfectly nowadays.  
But if you wanna build your own spider with legacy version, please check the `legacy` branch.

The difference between `legacy version` and `ng version`(New Generation):  
1. `legacy version` use `requests` to send requests, but `ng version` use webdriver.
2. `legacy version` cannot handle the page with code confusion.
3. `legacy version` is faster to get the data if no code confusion.

## Fix list:
- [x] [manaba] course list @ 7/28/2018
- [x] [manaba] better performance @ 1/28/2019
- [ ] [syllabus] ritsumei syllabus -> manaba syllabus
- [ ] [syllabus] get syllabus by id

## New feature:
- [ ] [syllabus] search syllabus by string
- [ ] [compusweb] scholarship information
- [ ] [compusweb] final test information
- [ ] [compusweb] grade information

# License
__GPLv3__

# How to import?
1. Install Python 3.  
Recommended Python Version: 3.7.1+
2. Install `nobo` with `pip` / `pip3`

    ```bash
    pip3 install nobo
    ```
3. Install latest version of Chrome and ChromeDriver
   - [Chrome](https://www.google.com/chrome/), latest version is recommended
   - [ChromeDriver](http://chromedriver.chromium.org/downloads), unzip and move `chromedriver`/`chromedriver.exe` into your project directory.
4. Use **nobo** in your project (.py).

    ```python
    import nobo
    # if you wanna output in an easy way
    import nobo.io
    ```

# Manaba Spider
It seems that Manaba of each school are different, you can change a little bit code inside [manaba.py](manaba.py) to let nobo be compatible with your manaba page.

## How to use
1. Create a `RitsStudent` instance.

    ```python
    # The following username and password is not real :)
    fangzhou = nobo.RitsStudent("is0000ab", "12345678")
    ```

2. Use `get_course_list()` method to get all courses information.  
`get_course_list()` will login automatically. After parsing, it will return a list that contains all information of courses.

    ```python
    try:
        course_list = fangzhou.get_course_list()
        nobo.io.export_as_json("temp.json", course_list)
    except:
        exit()
    ```

## Course list example
The example course will show as following.

```json
[
    {
        "basic": [
            {
                "code": 33698,
                "name": "ソフトインテリジェンス",
                "class": "D1"
            }
        ],
        "time": {
            "year": 2018,
            "semester": "fall",
            "weekday": "Wednesday",
            "period": "2",
            "sci_period_start": "3",
            "sci_period_end": "4"
        },
        "room": "C402",
        "teacher": [
            "前田 陽一郎"
        ]
    },
    {
        ...
        other courses
        ...
    }
]
```
