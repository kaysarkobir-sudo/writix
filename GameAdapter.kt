package com.writixai.games

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class GameAdapter(
    private var games: List<Game>,
    private var favorites: Set<String>,
    private val listener: Listener
) : RecyclerView.Adapter<GameAdapter.GameViewHolder>() {

    interface Listener {
        fun onOpen(game: Game)
        fun onToggleFavorite(game: Game)
    }

    class GameViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val gameName: TextView = view.findViewById(R.id.gameName)
        val gameCategory: TextView = view.findViewById(R.id.gameCategory)
        val favoriteBtn: ImageButton = view.findViewById(R.id.favoriteBtn)
        val root: View = view
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): GameViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_game, parent, false)
        return GameViewHolder(view)
    }

    override fun onBindViewHolder(holder: GameViewHolder, position: Int) {
        val game = games[position]

        holder.gameName.text = game.name
        holder.gameCategory.text = game.category ?: "Uncategorized"

        // Update favorite button icon
        val isFavorite = favorites.contains(game.id)
        holder.favoriteBtn.setImageResource(
            if (isFavorite) R.drawable.ic_favorite else R.drawable.ic_favorite_border
        )

        // Set click listener for opening the game
        holder.root.setOnClickListener {
            listener.onOpen(game)
        }

        // Set click listener for favorite button
        holder.favoriteBtn.setOnClickListener {
            listener.onToggleFavorite(game)
        }
    }

    override fun getItemCount(): Int = games.size

    fun update(newGames: List<Game>, newFavorites: Set<String>) {
        this.games = newGames
        this.favorites = newFavorites
        notifyDataSetChanged()
    }
}
