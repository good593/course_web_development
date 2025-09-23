// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 폼과 입력 요소들 가져오기
    const form = document.querySelector('form');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // 검증 규칙 정의
    const validationRules = {
        name: {
            minLength: 2,
            maxLength: 20,
            pattern: /^[가-힣a-zA-Z\s]+$/, // 한글, 영문, 공백만 허용
            errorMessages: {
                required: '이름을 입력해주세요.',
                minLength: '이름은 최소 2자 이상이어야 합니다.',
                maxLength: '이름은 최대 20자까지 가능합니다.',
                pattern: '이름은 한글 또는 영문만 입력 가능합니다.'
            }
        },
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, // 기본적인 이메일 패턴
            errorMessages: {
                required: '이메일을 입력해주세요.',
                pattern: '올바른 이메일 형식을 입력해주세요.'
            }
        },
        password: {
            minLength: 8,
            maxLength: 20,
            pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/, // 대소문자, 숫자, 특수문자 포함
            errorMessages: {
                required: '비밀번호를 입력해주세요.',
                minLength: '비밀번호는 최소 8자 이상이어야 합니다.',
                maxLength: '비밀번호는 최대 20자까지 가능합니다.',
                pattern: '비밀번호는 대문자, 소문자, 숫자, 특수문자를 각각 하나 이상 포함해야 합니다.'
            }
        }
    };

    /**
     * 오류 메시지를 표시하는 함수
     */
    function showError(input, message) {
        // 기존 오류 메시지 제거
        removeError(input);
        
        // 입력창에 오류 스타일 적용
        input.classList.add('border-red-500', 'focus:ring-red-500');
        input.classList.remove('border-gray-300', 'focus:ring-blue-500');
        
        // 오류 메시지 요소 생성
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message text-red-500 text-sm mt-1';
        errorElement.textContent = message;
        
        // 입력창 다음에 오류 메시지 삽입
        input.parentNode.insertBefore(errorElement, input.nextSibling);
    }

    /**
     * 오류 메시지를 제거하는 함수
     */
    function removeError(input) {
        // 입력창 스타일을 정상으로 복원
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-300', 'focus:ring-blue-500');
        
        // 기존 오류 메시지 제거
        const errorElement = input.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * 성공 스타일을 적용하는 함수
     */
    function showSuccess(input) {
        removeError(input);
        input.classList.add('border-green-500', 'focus:ring-green-500');
        input.classList.remove('border-gray-300', 'focus:ring-blue-500');
    }

    /**
     * 개별 입력값을 검증하는 함수
     */
    function validateField(input, fieldName) {
        const value = input.value.trim();
        const rules = validationRules[fieldName];

        // 필수 입력 검증
        if (!value) {
            showError(input, rules.errorMessages.required);
            return false;
        }

        // 최소 길이 검증
        if (rules.minLength && value.length < rules.minLength) {
            showError(input, rules.errorMessages.minLength);
            return false;
        }

        // 최대 길이 검증
        if (rules.maxLength && value.length > rules.maxLength) {
            showError(input, rules.errorMessages.maxLength);
            return false;
        }

        // 패턴 검증
        if (rules.pattern && !rules.pattern.test(value)) {
            showError(input, rules.errorMessages.pattern);
            return false;
        }

        // 모든 검증 통과
        showSuccess(input);
        return true;
    }

    /**
     * 전체 폼을 검증하는 함수
     */
    function validateForm() {
        const nameValid = validateField(nameInput, 'name');
        const emailValid = validateField(emailInput, 'email');
        const passwordValid = validateField(passwordInput, 'password');

        return nameValid && emailValid && passwordValid;
    }

    // 실시간 검증 이벤트 리스너 등록
    nameInput.addEventListener('blur', function() {
        validateField(this, 'name');
    });

    emailInput.addEventListener('blur', function() {
        validateField(this, 'email');
    });

    passwordInput.addEventListener('blur', function() {
        validateField(this, 'password');
    });

    // 입력 중일 때 오류 메시지 제거 (사용자 경험 개선)
    nameInput.addEventListener('input', function() {
        if (this.parentNode.querySelector('.error-message')) {
            removeError(this);
        }
    });

    emailInput.addEventListener('input', function() {
        if (this.parentNode.querySelector('.error-message')) {
            removeError(this);
        }
    });

    passwordInput.addEventListener('input', function() {
        if (this.parentNode.querySelector('.error-message')) {
            removeError(this);
        }
    });

    // 폼 제출 시 검증
    form.addEventListener('submit', function(e) {
        e.preventDefault(); // 기본 제출 동작 방지

        // 전체 폼 검증
        if (validateForm()) {
            // 검증 성공 시 처리
            alert('회원가입이 완료되었습니다!');
            console.log('폼 데이터:', {
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                password: passwordInput.value
            });
            
            // 실제 서버로 데이터 전송하는 코드를 여기에 추가
            // 예: fetch('/api/signup', { method: 'POST', body: formData })
        } else {
            // 검증 실패 시 첫 번째 오류 필드로 포커스 이동
            const firstErrorField = form.querySelector('.border-red-500');
            if (firstErrorField) {
                firstErrorField.focus();
            }
        }
    });

    // 비밀번호 강도 표시 기능 (선택사항)
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;
        let strengthText = '';
        let strengthColor = '';

        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[@$!%*?&]/.test(password)) strength++;

        // 기존 강도 표시 제거
        const existingStrength = this.parentNode.querySelector('.password-strength');
        if (existingStrength) {
            existingStrength.remove();
        }

        if (password.length > 0) {
            switch (strength) {
                case 1:
                case 2:
                    strengthText = '약함';
                    strengthColor = 'text-red-500';
                    break;
                case 3:
                case 4:
                    strengthText = '보통';
                    strengthColor = 'text-yellow-500';
                    break;
                case 5:
                    strengthText = '강함';
                    strengthColor = 'text-green-500';
                    break;
            }

            // 강도 표시 요소 생성
            const strengthElement = document.createElement('div');
            strengthElement.className = `password-strength text-sm mt-1 ${strengthColor}`;
            strengthElement.textContent = `비밀번호 강도: ${strengthText}`;
            
            // 비밀번호 입력창 다음에 삽입
            this.parentNode.insertBefore(strengthElement, this.nextSibling);
        }
    });
});

