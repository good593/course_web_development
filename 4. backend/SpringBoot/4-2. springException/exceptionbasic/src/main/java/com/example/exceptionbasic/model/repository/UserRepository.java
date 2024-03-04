package com.example.exceptionbasic.model.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.exceptionbasic.model.dto.UserDto;

public interface UserRepository extends JpaRepository<UserDto, String> {
    
}
