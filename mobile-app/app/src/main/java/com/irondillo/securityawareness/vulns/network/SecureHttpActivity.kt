package com.irondillo.securityawareness.vulns.network

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.net.URL
import javax.net.ssl.HttpsURLConnection

class SecureHttpActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val url = URL("https://example.com")
        val conn = url.openConnection() as HttpsURLConnection
        conn.inputStream
    }
}
