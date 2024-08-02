// 데이터 및 화면 초기화
function initPomodoro() {
    init();
    startEl.addEventListener("click", startTimeOfPomodoro);
    resetEl.addEventListener("click", resetTimerOfPomodoro);

    interval = null; // 값이 없음. 즉, false
    timeLeft = 1500; // 25분(1500초)
    updateTimeOfPomodoro();
    titleEl.innerHTML = "Pomodoro Timer";
    stopTimer();
}

function removeListenrAllOfPomodoro() {
    startEl.removeEventListener("click", startTimeOfPomodoro);
    resetEl.removeEventListener("click", resetTimerOfPomodoro);
}

function updateTimeOfPomodoro() {
    let minutes = Math.floor(timeLeft / 60); // 초 / 60 -> 분!!
    let seconds = timeLeft % 60; // 초 % 60 -> 나눈값의 나머지는 초!!!
    let formattedTime = `${minutes.toString().padStart(2, "0")}:${seconds
        .toString()
        .padStart(2, "0")}`;

    // 남의 시간이 변경되는 코드....
    timerEl.innerHTML = formattedTime;
}

function startTimeOfPomodoro() {
    // 기존 setInterval이 존재하면 제거하는 로직!!
    if (interval) {
    stopTimer();
    }
    // interval = setInterval의 식별할 수 있는 index 반환 
    // setInterval: 특정 시간 단위로 어떤 함수를 계속 실행함!!!
    interval = setInterval(() => {
        timeLeft--; // 함수가 실행될때마다 하나씩 줄어듬..
        // updateTimer를 통해서 화면에 변경된 시간을 적용!!!
        updateTimeOfPomodoro();
        // 남은 시간이 0초가 되면, 더 이상 함수를 실행하지 않음!!
        if (timeLeft === 0) {
            alert("Time's up!");
            resetTimerOfPomodoro();
        }
    }, 1000); // 1초에 한번씩 함수실행!!
}

function resetTimerOfPomodoro() {
    // 기존에 있는 setInterval를 제거 
    stopTimer();
    // 데이터 및 화면 초기화
    initPomodoro();
}

