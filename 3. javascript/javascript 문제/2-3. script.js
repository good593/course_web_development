document.addEventListener("DOMContentLoaded", function () {
  // [1] 본문 영역(오늘의 이야기 카드 본문) 찾기
  const mainText = document.querySelector("article .card-text");

  // [2] "본문 내용 바꾸기" 버튼 만들기
  const changeTextBtn = document.createElement("button");
  changeTextBtn.textContent = "본문 내용 바꾸기";
  changeTextBtn.className = "btn btn-primary m-1"; // Bootstrap 버튼 스타일
  document.body.appendChild(changeTextBtn);

  // 버튼 클릭 시 본문 내용을 변경
  changeTextBtn.addEventListener("click", function () {
    mainText.textContent = "자바스크립트를 이용해서 본문 내용을 바꿨습니다!";
  });

  // [3] "본문 색상 바꾸기" 버튼 만들기
  const changeColorBtn = document.createElement("button");
  changeColorBtn.textContent = "본문 색상 바꾸기";
  changeColorBtn.className = "btn btn-success m-1";
  document.body.appendChild(changeColorBtn);

  // 버튼 클릭 시 본문 글자 색상을 변경
  changeColorBtn.addEventListener("click", function () {
    mainText.style.color = "crimson"; // 글자색을 빨간색 계열로 변경
  });
});
