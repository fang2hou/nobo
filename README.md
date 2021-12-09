# nobo (No Borders)

Note: *This is a personal open source project. Please use `nobo` at your own risk.*

**nobo** is a spider that you could get your data from each service provides by Ritsumeikan Univ.
You can use **nobo** to build your own data API with many frameworks(`Flask`, `Django` etc.).


## Requirements

- [Chrome](https://www.google.com/chrome/)
- [ChromeDriver](http://chromedriver.chromium.org/downloads)

Note: *Latest version of Chrome and ChromeDriver* is recommended.

## Install

### From source

```bash
git clone --depth 1 https://github.com/eggplants/nobo && cd nobo
pip install -e .
```

### From PyPI

```bash
pip install nobo
```

## Usage

```python
import nobo
fangzhou = nobo.RitsStudent("is0000ab", "12345678")
course_list = fangzhou.get_course_list()
nobo.io.export_as_json("temp.json", course_list)
```

returns:

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

## For other Univ

It seems that Manaba of each school are different, you can change a little bit code inside
[manaba.py](nobo/manaba.py) to let nobo be compatible with your manaba page.

## License

GPLv3
