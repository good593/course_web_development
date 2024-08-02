const startEl = document.getElementById("start");
const stopEl = document.getElementById("stop");
const resetEl = document.getElementById("reset");
const stopwatchEl = document.getElementById("stopwatch");
const pomodoroEl = document.getElementById("pomodoro");

const titleEl = document.getElementById("title");
const timerEl = document.getElementById("timer");

let interval;
let timeLeft; 

function init() {
    if (interval) {
        stopTimer();
    }
    removeListenrAllOfPomodoro();
    removeListenrAllOfStopwatch();
}

function stopTimer() {
    if(interval) {
        clearInterval(interval);
    }
}

stopEl.addEventListener("click", stopTimer);
stopwatchEl.addEventListener("click", initStopwatch);
pomodoroEl.addEventListener("click", initPomodoro);
initPomodoro();