package com.irondillo.securityawareness.vulns.auth

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/**
 * Demonstrates a weak password policy with minimal checks.
 */
class WeakPasswordActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val password = "123"
        if (password.length > 3) {
            Toast.makeText(this, "Password accepted", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Password too short", Toast.LENGTH_SHORT).show()
        }
    }
}

