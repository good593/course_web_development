package com.example.exceptionbasic.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.exceptionbasic.exception.UserException;
import com.example.exceptionbasic.model.dto.UserDto;
import com.example.exceptionbasic.model.repository.UserRepository;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;

    public void insertUser(UserDto dto) throws Exception {
        log.info("[UserService][insertUser] dto >> "+dto.toString());
        
        if(!dto.getUserType().equals("일반사용자") 
            && !dto.getUserType().equals("관리자") 
            && !dto.getUserType().equals("매니저")) {
            throw new UserException("유저 종류 오류");
        }

        userRepository.save(dto);
    }

    public UserDto selectByUserName(String userName) throws Exception {
        return userRepository.getReferenceById(userName);
    }

}
