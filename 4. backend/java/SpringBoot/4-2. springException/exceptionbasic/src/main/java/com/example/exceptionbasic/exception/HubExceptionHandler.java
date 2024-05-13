package com.example.exceptionbasic.exception;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestControllerAdvice
public class HubExceptionHandler {
    
    @ExceptionHandler(value = UserException.class)
    public ResponseEntity<Map<String, Object>> userExceptionHandler(UserException e) {
        log.info("[HubExceptionHandler][userExceptionHandler] e.getMessage() > "+e.getMessage());

        HttpHeaders httpHeaders = new HttpHeaders();
        HttpStatus httpStatus = HttpStatus.BAD_REQUEST;
        Map<String, Object> map = new HashMap<>();
        map.put("exceptionType", "UserException");
        map.put("msg","사용자 오류발생");

        return new ResponseEntity<>(map, httpHeaders, httpStatus);
    }

    @ExceptionHandler(value = Exception.class)
    public ResponseEntity<Map<String, Object>> exceptionHandler(Exception e) {
        log.info("[HubExceptionHandler][exceptionHandler] e.getMessage() > "+e.getMessage());

        HttpHeaders httpHeaders = new HttpHeaders();
        HttpStatus httpStatus = HttpStatus.EXPECTATION_FAILED;
        Map<String, Object> map = new HashMap<>();
        map.put("exceptionType", "Exception");
        map.put("msg","일반 오류발생");

        return new ResponseEntity<>(map, httpHeaders, httpStatus);
    }
}
