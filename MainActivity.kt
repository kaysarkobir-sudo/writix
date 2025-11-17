
package com.writixai.games

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class MainActivity : AppCompatActivity(), GameAdapter.Listener {

    private lateinit var adapter: GameAdapter
    private lateinit var prefs: SharedPreferences
    private lateinit var search: SearchView
    private lateinit var favSwitch: Switch

    private var allGames: MutableList<Game> = mutableListOf()
    private var favorites: MutableSet<String> = mutableSetOf()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences("writixai", MODE_PRIVATE)
        favorites = prefs.getStringSet("favorites", emptySet())?.toMutableSet() ?: mutableSetOf()

        // Load JSON
        val json = resources.openRawResource(R.raw.games).bufferedReader().use { it.readText() }
        val type = object : TypeToken<List<Game>>() {}.type
        allGames = Gson().fromJson<List<Game>>(json, type).toMutableList()

        val recycler = findViewById<RecyclerView>(R.id.recycler)
        recycler.layoutManager = LinearLayoutManager(this)
        adapter = GameAdapter(allGames, favorites, this)
        recycler.adapter = adapter

        search = findViewById(R.id.search)
        favSwitch = findViewById(R.id.switchFavorites)
        favSwitch.setOnCheckedChangeListener { _, isChecked ->
            filter(query = search.query?.toString() ?: "", onlyFavs = isChecked)
        }

        search.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean { return true }
            override fun onQueryTextChange(newText: String?): Boolean {
                filter(query = newText ?: "", onlyFavs = favSwitch.isChecked)
                return true
            }
        })

        val bottom = findViewById<BottomNavigationView>(R.id.bottomNav)
        bottom.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_games -> true
                R.id.nav_calculator -> {
                    startActivity(Intent(this, CalculatorActivity::class.java))
                    true
                }
                R.id.nav_about -> {
                    startActivity(Intent(this, AboutActivity::class.java))
                    true
                }
                else -> false
            }
        }
    }

    private fun filter(query: String, onlyFavs: Boolean) {
        val q = query.lowercase()
        val filtered = allGames.filter { g ->
            val matches = g.name.lowercase().contains(q) ||
                (g.category ?: "").lowercase().contains(q) ||
                g.id.lowercase().contains(q)
            val favOk = if (onlyFavs) favorites.contains(g.id) else true
            matches && favOk
        }
        adapter.update(filtered, favorites)
    }

    override fun onOpen(game: Game) {
        val i = Intent(this, WebActivity::class.java)
        i.putExtra("title", game.name)
        i.putExtra("url", game.url)
        startActivity(i)
    }

    override fun onToggleFavorite(game: Game) {
        if (favorites.contains(game.id)) favorites.remove(game.id) else favorites.add(game.id)
        prefs.edit().putStringSet("favorites", favorites).apply()
        filter(query = search.query?.toString() ?: "", onlyFavs = favSwitch.isChecked)
    }
}
