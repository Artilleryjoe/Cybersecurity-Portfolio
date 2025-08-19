package com.irondillo.securityawareness.vulns.storage

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.security.MessageDigest

class SecurePrefsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("creds", MODE_PRIVATE)
        val hashed = MessageDigest.getInstance("SHA-256")
            .digest("123456".toByteArray())
            .joinToString("") { "%02x".format(it) }
        prefs.edit().putString("password_hash", hashed).apply()
    }
}
