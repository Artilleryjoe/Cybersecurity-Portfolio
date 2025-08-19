package com.irondillo.securityawareness.vulns.auth

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class WeakPasswordActivity : AppCompatActivity() {
    fun isValid(password: String) = password.length > 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        isValid("123")
    }
}
