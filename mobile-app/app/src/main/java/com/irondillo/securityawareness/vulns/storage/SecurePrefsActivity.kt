package com.irondillo.securityawareness.vulns.storage

import android.content.Context
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.security.MessageDigest

/**
 * Demonstrates hashing a password before storing it.
 */
class SecurePrefsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val password = "superSecret123"
        val hash = MessageDigest.getInstance("SHA-256")
            .digest(password.toByteArray())
            .joinToString("") { "%02x".format(it) }
        val prefs = getSharedPreferences("creds", Context.MODE_PRIVATE)
        prefs.edit().putString("password_hash", hash).apply()
    }
}

