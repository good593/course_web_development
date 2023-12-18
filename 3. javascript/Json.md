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
# [Json(JavaScript Object Notation)](https://ko.javascript.info/json)
- JSON은 본래 자바스크립트에서 사용할 목적으로 만들어진 포맷입니다. 그런데 라이브러리를 사용하면 자바스크립트가 아닌 언어에서도 JSON을 데이터 교환 목적으로 사용하는 경우가 많습니다. 
- 특히 클라이언트 측 언어가 자바스크립트일 때 말이죠. 서버 측 언어는 무엇이든 상관없습니다.

자바스크립트가 제공하는 JSON 관련 메서드는 아래와 같습니다.
- JSON.stringify: 객체를 JSON으로 바꿔줍니다.
- JSON.parse: JSON을 객체로 바꿔줍니다.

---
### JSON.stringify

```javascript
let student = {
  name: 'John',
  age: 30,
  isAdmin: false,
  courses: ['html', 'css', 'js'],
  wife: null
};

let json = JSON.stringify(student);

alert(typeof json); // 문자열이네요!

alert(json);
```

---
```javascript
let meetup = {
  title: "Conference",
  room: {
    number: 23,
    participants: ["john", "ann"]
  }
};

alert( JSON.stringify(meetup) );
```

---
### JSON.parse

```javascript
// 문자열로 변환된 배열
let numbers = "[0, 1, 2, 3]";

numbers = JSON.parse(numbers);

alert( numbers[1] ); // 1
```

```javascript
let userData = '{ "name": "John", "age": 35, "isAdmin": false, "friends": [0,1,2,3] }';

let user = JSON.parse(userData);

alert( user.friends[1] ); // 1
```

---
### reviver

```javascript
let str = '{"title":"Conference","date":"2017-11-30T12:00:00.000Z"}';

let meetup = JSON.parse(str);

alert( meetup.date.getDate() ); // 에러!
```
meetup.date의 값은 Date 객체가 아니고 문자열이기 때문에 발생한 에러입니다. 그렇다면 문자열을 Date로 전환해줘야 한다는 걸 어떻게 JSON.parse에게 알릴 수 있을까요?

이럴 때 JSON.parse의 두 번째 인수 reviver를 사용하면 됩니다. 모든 값은 “그대로”, 하지만 date만큼은 Date 객체를 반환하도록 함수를 구현해 봅시다.

---
```javascript
let str = '{"title":"Conference","date":"2017-11-30T12:00:00.000Z"}';

let meetup = JSON.parse(str, function(key, value) {
  if (key == 'date') return new Date(value);
  return value;
});

alert( meetup.date.getDate() ); // 이제 제대로 동작하네요!
```
```javascript
let schedule = `{
  "meetups": [
    {"title":"Conference","date":"2017-11-30T12:00:00.000Z"},
    {"title":"Birthday","date":"2017-04-18T12:00:00.000Z"}
  ]
}`;

schedule = JSON.parse(schedule, function(key, value) {
  if (key == 'date') return new Date(value);
  return value;
});

alert( schedule.meetups[1].date.getDate() ); // 잘 동작합니다!
```








