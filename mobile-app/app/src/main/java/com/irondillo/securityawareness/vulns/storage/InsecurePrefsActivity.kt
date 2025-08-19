package com.irondillo.securityawareness.vulns.storage

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class InsecurePrefsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("creds", MODE_PRIVATE)
        prefs.edit().putString("password", "123456").apply()
    }
}
