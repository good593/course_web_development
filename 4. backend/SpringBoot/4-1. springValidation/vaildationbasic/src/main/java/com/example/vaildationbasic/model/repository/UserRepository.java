package com.example.vaildationbasic.model.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.vaildationbasic.model.entity.UserEntity;

public interface UserRepository extends JpaRepository<UserEntity, String> {
    
}
