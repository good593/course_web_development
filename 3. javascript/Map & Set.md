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
# [Map & Set](https://ko.javascript.info/map-set)
지금까진 아래와 같은 복잡한 자료구조를 학습해 보았습니다.
- 객체: 키가 있는 컬렉션을 저장함
- 배열: 순서가 있는 컬렉션을 저장함
    
하지만 현실 세계를 반영하기엔 이 두 자료구조 만으론 부족해서 맵(Map)과 셋(Set)이 등장하게 되었습니다.

---
# [Map](https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Global_Objects/Map)
맵(Map)은 키가 있는 데이터를 저장한다는 점에서 객체와 유사합니다. 다만, 맵은 키에 다양한 자료형을 허용한다는 점에서 차이가 있습니다.

---
맵에는 다음과 같은 주요 메서드와 프로퍼티가 있습니다.
- `new Map()`: 맵을 만듭니다.
- `map.set(key, value)`: key를 이용해 value를 저장합니다.
- `map.get(key)`: key에 해당하는 값을 반환합니다. key가 존재하지 않으면 undefined를 반환합니다.
- `map.has(key)`: key가 존재하면 true, 존재하지 않으면 false를 반환합니다.
- `map.delete(key)`: key에 해당하는 값을 삭제합니다.
- `map.clear()`: 맵 안의 모든 요소를 제거합니다.
- `map.size`: 요소의 개수를 반환합니다.

---
```javascript
let map = new Map();

map.set('1', 'str1');   // 문자형 키
map.set(1, 'num1');     // 숫자형 키
map.set(true, 'bool1'); // 불린형 키

// 객체는 키를 문자형으로 변환한다는 걸 기억하고 계신가요?
// 맵은 키의 타입을 변환시키지 않고 그대로 유지합니다. 따라서 아래의 코드는 출력되는 값이 다릅니다.
alert( map.get(1)   ); // 'num1'
alert( map.get('1') ); // 'str1'

alert( map.size ); // 3
```
---
```javascript
let john = { name: "John" };

// 고객의 가게 방문 횟수를 세본다고 가정해 봅시다.
let visitsCountMap = new Map();

// john을 맵의 키로 사용하겠습니다.
visitsCountMap.set(john, 123);

alert( visitsCountMap.get(john) ); // 123
```

```javascript
let john = { name: "John" };

let visitsCountObj = {}; // 객체를 하나 만듭니다.

visitsCountObj[john] = 123; // 객체(john)를 키로 해서 객체에 값(123)을 저장해봅시다.

// 원하는 값(123)을 얻으려면 아래와 같이 키가 들어갈 자리에 `object Object`를 써줘야합니다.
alert( visitsCountObj["[object Object]"] ); // 123
```
---
### 체이닝  
> map.set 을 호출할 때마다 맵 자신이 반환됩니다. 이를 이용하면 map.set을 '체이닝(chaining)`할 수 있습니다.

```javascript
let map = new Map();

map.set('1', 'str1').set(1, 'num1').set(ture, 'bool1');
```
---
### 맵의 요소에 반복 작업하기    
다음 세 가지 메서드를 사용해 맵의 각 요소에 반복 작업을 할 수 있습니다.
  - `map.keys()`: 각 요소의 키를 모은 반복 가능한(iterable, 이터러블) 객체를 반환합니다.
  - `map.values()`: 각 요소의 값을 모은 이터러블 객체를 반환합니다.
  - `map.entries()`: 요소의 [키, 값]을 한 쌍으로 하는 이터러블 객체를 반환합니다. 이 이터러블 객체는 for..of반복문의 기초로 쓰입니다.

```javascript
let recipeMap = new Map([
  ['cucumber', 500],
  ['tomatoes', 350],
  ['onion',    50]
]);
```

---
```javascript
// 키(vegetable)를 대상으로 순회합니다.
for (let vegetable of recipeMap.keys()) {
  alert(vegetable); // cucumber, tomatoes, onion
}

// 값(amount)을 대상으로 순회합니다.
for (let amount of recipeMap.values()) {
  alert(amount); // 500, 350, 50
}

// [키, 값] 쌍을 대상으로 순회합니다.
for (let entry of recipeMap) { // recipeMap.entries()와 동일합니다.
  alert(entry); // cucumber,500 ...
}

// 각 (키, 값) 쌍을 대상으로 함수를 실행
recipeMap.forEach( (value, key, map) => {
  alert(`${key}: ${value}`); // cucumber: 500 ...
});
```
---
# Set
셋(Set)은 중복을 허용하지 않는 값을 모아놓은 특별한 컬렉션입니다. 셋에 키가 없는 값이 저장됩니다.

주요 메서드는 다음과 같습니다.
- `new Set(iterable)`: 셋을 만듭니다. 이터러블 객체를 전달받으면(대개 배열을 전달받음) 그 안의 값을 복사해 셋에 넣어줍니다.
- `set.add(value)`: 값을 추가하고 셋 자신을 반환합니다.
- `set.delete(value)`: 값을 제거합니다. 호출 시점에 셋 내에 값이 있어서 제거에 성공하면 true, 아니면 false를 반환합니다.
- `set.has(value)`: 셋 내에 값이 존재하면 true, 아니면 false를 반환합니다.
- `set.clear()`: 셋을 비웁니다.
- `set.size`: 셋에 몇 개의 값이 있는지 세줍니다.

---
```javascript
let set = new Set();

let john = { name: "John" };
let pete = { name: "Pete" };
let mary = { name: "Mary" };

// 어떤 고객(john, mary)은 여러 번 방문할 수 있습니다.
set.add(john);
set.add(pete);
set.add(mary);
set.add(john);
set.add(mary);

// 셋에는 유일무이한 값만 저장됩니다.
alert( set.size ); // 3

for (let user of set) {
  alert(user.name); // // John, Pete, Mary 순으로 출력됩니다.
}
```
---
- 셋의 값에 반복 작업하기 

```javascript
let set = new Set(["oranges", "apples", "bananas"]);

for (let value of set) alert(value);

// forEach를 사용해도 동일하게 동작합니다.
set.forEach((value, valueAgain, set) => {
  alert(value);
});
```









