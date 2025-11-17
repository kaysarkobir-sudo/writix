
package com.writixai.games

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class GameAdapter(
    private var items: List<Game>,
    private var favorites: Set<String>,
    private val listener: Listener
) : RecyclerView.Adapter<GameAdapter.VH>() {

    interface Listener {
        fun onOpen(game: Game)
        fun onToggleFavorite(game: Game)
    }

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val name: TextView = v.findViewById(R.id.title)
        val url: TextView = v.findViewById(R.id.url)
        val category: TextView = v.findViewById(R.id.category)
        val btnOpen: Button = v.findViewById(R.id.btnOpen)
        val btnFav: ImageButton = v.findViewById(R.id.btnFav)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_game, parent, false)
        return VH(view)
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: VH, position: Int) {
        val g = items[position]
        holder.name.text = g.name
        holder.url.text = g.url
        holder.category.text = g.category ?: "Game"
        holder.btnOpen.setOnClickListener { listener.onOpen(g) }
        val isFav = favorites.contains(g.id)
        holder.btnFav.setImageResource(if (isFav) android.R.drawable.btn_star_big_on else android.R.drawable.btn_star_big_off)
        holder.btnFav.setOnClickListener { listener.onToggleFavorite(g) }
    }

    fun update(newItems: List<Game>, favs: Set<String>) {
        items = newItems
        favorites = favs
        notifyDataSetChanged()
    }
}
