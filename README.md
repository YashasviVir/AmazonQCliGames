# 🕹️ Two Games Built with Amazon Q CLI — Match-3 & 2048

This repository contains two classic games—**a Match-3 Puzzle** and **2048**—completely generated using Amazon Q CLI. With just a few prompts and some light iteration, both games were built, refined, and made playable end-to-end through the power of Amazon Q.

I followed this excellent setup guide by [Ricardo Sueiras](https://community.aws/content/2v5PptEEYT2y0lRmZbFQtECA66M/the-essential-guide-to-installing-amazon-q-developer-cli-on-windows?trk=e07eca93-fa2f-4351-b567-f293b83eb635&sc_channel=el_) to get started, and you can read about my full experience in this [blog post](https://community.aws/content/2xcHGWx6W6RUPP0a9wzxSFEgqQh/how-i-built-two-games-in-under-an-hour-with-amazon-q-cli).


## 🎮 Match-3 Puzzle Game

A colorful tile-matching game inspired by *Candy Crush*. Players swap adjacent gems to create matches of three or more in a row. This version includes scoring, polished visuals, smooth animations, and error handling for invalid swaps.

- Built using `pygame`
- Grid-based mechanics with animated gem swapping
- Responsive UI with design customization
- Score tracking and gem clearing


## 🧠 2048 Game

A full implementation of the addictive sliding tile puzzle game. Combine matching number tiles to reach 2048—and beyond. Built in a single prompt, this version is highly responsive and true to the original.

- Built using `pygame`
- Classic 4x4 tile grid with smooth slide animations
- Score and best score tracking
- Game over detection and "keep playing" mode
