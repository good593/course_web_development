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
# [HTML Element](https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML/Getting_started)

---
### [Item elements]((https://developer.mozilla.org/en-US/docs/Web/HTML/Inline_elements))
브라우저에 컨텐츠가 없어도 보이는 태그 또는 컨텐츠를 꾸며주는 태그
- a, video, button, audio, input, map, label, canvas, img, table 등

```html
<p>
  This span is an <span class="highlight">inline-level element</span>; its
  background has been colored to display both the beginning and end of the
  element's influence. Input elements, like <input type="radio" /> and
  <input type="checkbox" />, are also inline-level content.
</p>
```

---
### [Box elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements)
브라우저에 컨텐츠가 없으면 보이지 않는 태그 또는 영역이나 의미를 정의하는 태그
- header, section, footer, article, nav, div, aside, span, main, form, h1 등

```html
<div>
  <p>
    This the first paragraph. The background color of these paragraphs have been
    colored to distinguish them from their parent element.
  </p>
  <p>This is the second paragraph.</p>
</div>

```

---
# [Block Or Inline](https://blog.4psa.com/css-display-and-the-basic-box-model/)
HTML 요소는 인라인 또는 블록이라는 두 가지 매우 다른 방식으로 표시될 수 있습니다. 

![alt text](./img/html/image.png)

---
### [예제1](https://stackoverflow.com/questions/75467117/root-inline-box-can-an-root-inline-box-have-descendants-in-turn-or-what-does-t)
```html
<div>
  In the case of <strong>Fire</strong>, break glass to 
  <span>sound alarm. <img src="bell.jpg" alt="bell symbol"></span>
</div>
```
![w:600](./img/html/image-1.png)

---
### [예제2](https://stackoverflow.com/questions/75776216/what-exactly-is-an-inline-box)
```html
<!doctype html>
<html>
  <body>
    <div>
      <span>Hello world</span>
      <img href="example.com" alt="an example">
    </div>
  </body>
</html>
```
---
![alt text](./img/html/image-2.png)


