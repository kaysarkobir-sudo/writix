
package com.writixai.games

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity

class AboutActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_about)
        supportActionBar?.title = "About"
    }

    fun openSite(v: View) { open("https://writixai.com") }
    fun openPrivacy(v: View) { open("https://writixai.com/privacy-policy/") }
    fun openTerms(v: View) { open("https://writixai.com/terms-and-conditions/") }

    private fun open(url: String) {
        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    }
}
