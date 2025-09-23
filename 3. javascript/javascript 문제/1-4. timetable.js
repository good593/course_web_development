document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector("table");
  const tbody = table.querySelector("tbody");
  const theadRow = table.querySelector("thead tr");

  let selectedCell = null; // 선택된 셀 저장 변수

  // 1) 셀 클릭하면 선택 표시
  table.addEventListener("click", function (e) {
    // td 또는 th 클릭 시 동작
    if (e.target.tagName === "TD" || e.target.tagName === "TH") {
      if (selectedCell) {
        selectedCell.classList.remove("selected");
      }
      selectedCell = e.target;
      selectedCell.classList.add("selected");
    }
  });

  // 2) 셀 더블클릭하면 내용 수정
  table.addEventListener("dblclick", function (e) {
    if (e.target.tagName === "TD") {
      const newText = prompt("새로운 과목을 입력하세요:", e.target.textContent);
      if (newText !== null) {
        e.target.textContent = newText;
      }
    }
  });

  // 3) 행 추가 버튼
  document.getElementById("addRow").addEventListener("click", function () {
    const newRow = document.createElement("tr");

    // 시간 입력받기
    const time = prompt("시간을 입력하세요 (예: 13:00 - 14:30):", "새 시간");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = time || "새 시간";
    newRow.appendChild(th);

    // 기존 요일 개수만큼 빈 칸(td) 추가
    const colCount = theadRow.children.length - 1; // 첫 번째는 시간
    for (let i = 0; i < colCount; i++) {
      const td = document.createElement("td");
      td.textContent = "";
      newRow.appendChild(td);
    }

    tbody.appendChild(newRow);
  });

  // 4) 열 추가 버튼
  document.getElementById("addCol").addEventListener("click", function () {
    const newDay = prompt("새 요일을 입력하세요:", "새 요일");

    // 헤더에 새로운 요일 추가
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = newDay || "새 요일";
    theadRow.appendChild(th);

    // 각 행에 빈 셀 추가
    tbody.querySelectorAll("tr").forEach((row) => {
      const td = document.createElement("td");
      td.textContent = "";
      row.appendChild(td);
    });
  });

  // 5) 선택된 셀 지우기 버튼
  document.getElementById("clearCell").addEventListener("click", function () {
    if (selectedCell) {
      selectedCell.textContent = "";
      selectedCell.classList.remove("selected");
      selectedCell = null;
    } else {
      alert("먼저 셀을 선택하세요!");
    }
  });
});

