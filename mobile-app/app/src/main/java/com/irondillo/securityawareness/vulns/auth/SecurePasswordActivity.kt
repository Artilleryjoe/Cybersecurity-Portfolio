package com.irondillo.securityawareness.vulns.auth

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class SecurePasswordActivity : AppCompatActivity() {
    fun isValid(password: String): Boolean {
        val lengthOk = password.length >= 8
        val hasDigit = password.any { it.isDigit() }
        val hasLetter = password.any { it.isLetter() }
        return lengthOk && hasDigit && hasLetter
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        isValid("P@ssw0rd")
    }
}
