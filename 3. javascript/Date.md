---
style: |
  img {
    display: block;
    float: none;
    margin-left: auto;
    margin-right: auto;
  }
marp: true
paginate: true
---
# [Date](https://ko.javascript.info/date)
### 생성하기
```javascript
let now = new Date();
alert( now ); // 현재 날짜 및 시간이 출력됨
```

```javascript
let date = new Date("2017-01-26");
alert(date);
```
---
- new Date(year, month, date, hours, minutes, seconds, ms)
> 주어진 인수를 조합해 만들 수 있는 날짜가 저장된 객체가 반환됩니다(지역 시간대 기준). 첫 번째와 두 번째 인수만 필수값입니다.

  - `year`는 반드시 네 자리 숫자여야 합니다. 2013은 괜찮고 98은 괜찮지 않습니다.
  - `month`는 0(1월)부터 11(12월) 사이의 숫자여야 합니다.
  - `date`는 일을 나타내는데, 값이 없는 경우엔 1일로 처리됩니다.
  - `hours/minutes/seconds/ms`에 값이 없는 경우엔 0으로 처리됩니다.

```javascript
new Date(2011, 0, 1, 0, 0, 0, 0); // 2011년 1월 1일, 00시 00분 00초
new Date(2011, 0, 1); // hours를 비롯한 인수는 기본값이 0이므로 위와 동일

let date = new Date(2011, 0, 1, 2, 3, 4, 567);
alert( date ); // 2011년 1월 1일, 02시 03분 04.567초
```
---
- UTC 기준(UTC+0) 1970년 1월 1일 0시 0분 0초에서 milliseconds 밀리초(1/1000 초) 후의 시점이 저장된 Date 객체가 반환됩니다.

```javascript
// 1970년 1월 1일 0시 0분 0초(UTC+0)를 나타내는 객체
let Jan01_1970 = new Date(0);
alert( Jan01_1970 );

// 1970년 1월 1일의 24시간 후는 1970년 1월 2일(UTC+0)임
let Jan02_1970 = new Date(24 * 3600 * 1000);
alert( Jan02_1970 );
```
---
### 날짜 구성요소 얻기
Date 객체의 메서드를 사용하면 연, 월, 일 등의 값을 얻을 수 있습니다.
- getFullYear()
> 연도(네 자릿수)를 반환합니다.
- getMonth()
> 월을 반환합니다(0 이상 11 이하).
- getDate()
> 일을 반환합니다(1 이상 31 이하). 어! 그런데 메서드 이름이 뭔가 이상하네요.
- getHours(), getMinutes(), getSeconds(), getMilliseconds()
> 시, 분, 초, 밀리초를 반환합니다.

---
- getDay()
> 일요일을 나타내는 0부터 토요일을 나타내는 6까지의 숫자 중 하나를 반환합니다.

위 메서드 이름에 있는 ‘get’ 다음에 'UTC’를 붙여주면 표준시(UTC+0) 기준의 날짜 구성 요소를 반환해주는 메서드 getUTCFullYear(), getUTCMonth(), getUTCDay()를 만들 수 있습니다.

```javascript
// 현재 일시
let date = new Date();

// 현지 시간 기준 시
alert( date.getHours() );

// 표준시간대(UTC+0, 일광 절약 시간제를 적용하지 않은 런던 시간) 기준 시
alert( date.getUTCHours() );
```
---
### 날짜 구성요소 설정하기 
- setFullYear(year, [month], [date])
- setMonth(month, [date])
- setDate(date)
- setHours(hour, [min], [sec], [ms])
- setMinutes(min, [sec], [ms])
- setSeconds(sec, [ms])
- setMilliseconds(ms)
- setTime(milliseconds) (1970년 1월 1일 00:00:00 UTC부터 밀리초 이후를 나타내는 날짜를 설정)

---
```javascript
let today = new Date();

today.setHours(0);
alert(today); // 날짜는 변경되지 않고 시만 0으로 변경됩니다.

today.setHours(0, 0, 0, 0);
alert(today); // 날짜는 변경되지 않고 시, 분, 초가 모두 변경됩니다(00시 00분 00초).
```
---
### 자동 고침 

```javascript
let date = new Date(2013, 0, 32); // 2013년 1월 32일은 없습니다.
alert(date); // 2013년 2월 1일이 출력됩니다.
```

```javascript
let date = new Date(2016, 1, 28);
date.setDate(date.getDate() + 2);

alert( date ); // 2016년 3월 1일
```

---
```javascript
let date = new Date();
date.setSeconds(date.getSeconds() + 70);

alert( date ); // 70초 후의 날짜가 출력됩니다.
```

```javascript
let date = new Date(2016, 0, 2); // 2016년 1월 2일

date.setDate(1); // 1일로 변경합니다.
alert( date ); // 01 Jan 2016

date.setDate(0); // 일의 최솟값은 1이므로 0을 입력하면 전 달의 마지막 날을 설정한 것과 같은 효과를 봅니다.
alert( date ); // 31 Dec 2015
```
---
### Date 객체를 숫자로 변경해 시간차 측정하기

```javascript
let date = new Date();
alert(+date); // 타임스탬프(date.getTime()를 호출한 것과 동일함)
```

```javascript
let start = new Date(); // 측정 시작

// 원하는 작업을 수행
for (let i = 0; i < 100000; i++) {
  let doSomething = i * i * i;
}

let end = new Date(); // 측정 종료

alert( `반복문을 모두 도는데 ${end - start} 밀리초가 걸렸습니다.` );
```

---
```javascript
let start = Date.now(); // 1970년 1월 1일부터 현재까지의 밀리초

// 원하는 작업을 수행
for (let i = 0; i < 100000; i++) {
  let doSomething = i * i * i;
}

let end = Date.now(); // done

alert( `반복문을 모두 도는데 ${end - start} 밀리초가 걸렸습니다.` ); // Date 객체가 아닌 숫자끼리 차감함
```
---
### Date.parse와 문자열 
메서드 [Date.parse(str)](https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Global_Objects/Date/parse)를 사용하면 문자열에서 날짜를 읽어올 수 있습니다.

단, 문자열의 형식은 `YYYY-MM-DDTHH:mm:ss.sssZ`처럼 생겨야 합니다.

- YYYY-MM-DD: 날짜(연-월-일)
- "T": 구분 기호로 쓰임
- HH:mm:ss.sss: 시:분:초.밀리초
- 'Z'(옵션): +-hh:mm 형식의 시간대를 나타냄. Z 한 글자인 경우엔 UTC+0을 나타냄

YYYY-MM-DD, YYYY-MM, YYYY같이 더 짧은 문자열 형식도 가능합니다.

---
위 조건을 만족하는 문자열을 대상으로 Date.parse(str)를 호출하면 문자열과 대응하는 날짜의 타임스탬프가 반환됩니다. 문자열의 형식이 조건에 맞지 않은 경우엔 NaN이 반환됩니다.

```javascript
let ms = Date.parse('2012-01-26T13:51:50.417-07:00');

alert(ms); // 1327611110417  (타임스탬프)
```

```javascript
let date = new Date( Date.parse('2012-01-26T13:51:50.417-07:00') );

alert(date);
```










