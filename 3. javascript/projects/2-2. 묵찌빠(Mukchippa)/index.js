const buttons = document.querySelectorAll("button");
const resultEl = document.getElementById("result");
const resultUserEL = document.getElementById("resultUser");
const resultComputerEL = document.getElementById("resultComputer");
const playerScoreEl = document.getElementById("user-score");
const computerScoreEl = document.getElementById("computer-score");
const gameObj = {
    "rock": "&#x1F44A;",
    "paper": "&#x1f590;",
    "scissors": "&#x270c;",
}

let mukchippaResult = {
    user: {
        score: 0,
        status: false,
        el: playerScoreEl
    },
    computer: {
        score: 0,
        status: false,
        el: computerScoreEl
    }
} 

buttons.forEach((button) => {
    button.addEventListener("click", () => {
        // playRound(사용자의 입력값, 컴퓨터의 입력값)
        let computerSelection = computerPlay();
        let result = playRound(button.id, computerSelection);
        resultEl.textContent = mukchippa(result);
        
        resultUserEL.innerHTML = "사용자: "+gameObj[button.id];
        resultUserEL.id = button.id;
        resultComputerEL.innerHTML = "컴퓨터: "+gameObj[computerSelection];
        resultComputerEL.id = computerSelection;
    });
});

function computerPlay() {
    const choices = ["rock", "paper", "scissors"];
    const randomChoice = Math.floor(Math.random() * choices.length);
    return choices[randomChoice];
}

function mukchippa(result) {
    if (!mukchippaResult['user']['status'] && !mukchippaResult['computer']['status']
            && result === "Tie") {
        return "Tie!"
    } 
    else if (mukchippaResult['user']['status'] && result === "Tie") {
        mukchippaResult['user']['score'] +=1;
        mukchippaResult['user']['el'].textContent = mukchippaResult['user']['score'];
        mukchippaResult['user']['status'] = false;
        return "You win!"
    }
    else if (mukchippaResult['computer']['status'] && result === "Tie") {
        mukchippaResult['computer']['score'] +=1;
        mukchippaResult['computer']['el'].textContent = mukchippaResult['computer']['score'];
        mukchippaResult['computer']['status'] = false;
        return "You lose!"
    }
    else {
        mukchippaResult['user']['status'] = false;
        mukchippaResult['computer']['status'] = false;
        mukchippaResult[result]['status'] = true;
        return `${result} attack Start!`;
    }
}

function playRound(playerSelection, computerSelection) {
    // 비겼을 때,
    if (playerSelection === computerSelection) {
        return "Tie";
    } 
    // 사용자가 이겼을 때, 
    else if (
        (playerSelection === "rock" && computerSelection === "scissors") ||
        (playerSelection === "paper" && computerSelection === "rock") ||
        (playerSelection === "scissors" && computerSelection === "paper")
    ) {
        return "user";
    } 
    // 컴퓨터가 이겼을 때, 
    else {
        return "computer";
    }
}