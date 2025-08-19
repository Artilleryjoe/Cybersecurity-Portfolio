package com.irondillo.securityawareness.vulns.auth

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/**
 * Demonstrates enforcing a stronger password policy.
 */
class StrongPasswordActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val password = "123"
        val strong = password.length >= 8 &&
            password.any { it.isDigit() } &&
            password.any { it.isLowerCase() } &&
            password.any { it.isUpperCase() }
        if (strong) {
            Toast.makeText(this, "Password accepted", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Weak password", Toast.LENGTH_SHORT).show()
        }
    }
}

