package com.irondillo.securityawareness.vulns.storage

import android.content.Context
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

/**
 * Demonstrates storing sensitive data in plain text SharedPreferences.
 */
class InsecurePrefsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("creds", Context.MODE_PRIVATE)
        // Password is stored in plain text
        prefs.edit().putString("password", "superSecret123").apply()
    }
}

