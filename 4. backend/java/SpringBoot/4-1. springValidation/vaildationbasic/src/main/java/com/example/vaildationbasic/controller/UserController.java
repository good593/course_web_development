package com.example.vaildationbasic.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.vaildationbasic.model.dto.UserDto;
import com.example.vaildationbasic.model.dto.UserValidDto;
import com.example.vaildationbasic.service.UserService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/user")
public class UserController {
    
    @Autowired
    private UserService uService;

    // localhost:8080/api/v1/user/select/test1
    @GetMapping("/select/{id}")
    public String getReferenceById(@PathVariable String id) {

        return uService.getReferenceById(id).toString();
    }

    // localhost:8080/api/v1/user/insert
    @PostMapping("/insert")
    public String insertUser(@RequestBody UserDto dto) {
        uService.insertUser(dto);
        return "저장 성공";
    }

    // localhost:8080/api/v1/user/insert/withtry
    @PostMapping("/insert/withtry")
    public String insertUserWithTry(@RequestBody UserDto dto) {
        try {
            if(dto.getPassword() == null || dto.getPassword().isEmpty()) {
                throw new Exception("버번이 없어요");
            }
            uService.insertUser(dto);
            return "저장 성공";
        } catch (Exception e) {
            // TODO: handle exception
            return "오류 발생 > "+e.getMessage();
        }
    }

    // localhost:8080/api/v1/user/insert/withvalid
    @PostMapping("/insert/withvalid")
    public String insertUserWithValid(@Valid @RequestBody UserValidDto dto) {

        uService.insertUserWithValid(dto);
        return "저장 성공";
    }

}
