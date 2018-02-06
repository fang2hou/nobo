# Nobo
"Nobo" means "No Borders", also means "登る" in Japanese.

This the first API that you could get your data from every service provides by Ritsumeikan Univ.

# License
__GPLv3__

__注意: 商用利用不可__

# Manaba API
## Requirement
`requests` , `BeautifulSoup4`, `re`, `json`

## How to use
1. Import the manaba class.

    ```python
    from manaba import *
    ```

2. Create an manabaUser object.

    ```python
    # The username and password is not real :)
    # Please initialized with an real account.
    fangzhou = manabaUser(username="is0000ab", password="12345678")
    ```

3. Use `login()` method to log in Manaba+R.

    ```python
    fangzhou.login()
    ```

4. Use `getCourseList()` method to get all courses information.

    ```python
    fangzhou.getCourseList()
    ```
    
5. Use `outputJSON("<ouputFileName>")` method to save data as JSON format.

    ```python
    fangzhou.outputJSON("test.json")
    ```

## Example data
The example course will show as following.

```json
[
    {
        "basic": [
            {
                "name": "(留)日本語Ⅷ(キャリア日本語b)",
                "code": "30819",
                "class": "G1"
            },
            {
                "name": "(留)日本語ⅩⅡ 口頭表現",
                "code": "30993",
                "class": "G1"
            }
        ],
        "teacher": [
            "久米 朋子"
        ],
        "time": {
            "year": 2017,
            "semester": "autumn",
            "weekday": "Monday",
            "period": "2"
        },
        "campus": "BKC",
        "room": "アドセミナリオ309号教室"
    },
]
```

# Syllabus API
In progress.


