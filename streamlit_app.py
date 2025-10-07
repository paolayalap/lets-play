import streamlit as st
import random

st.title("✊✋✌️ Piedra, Papel o Tijera")

choices = ["Piedra", "Papel", "Tijera"]
user_choice = st.radio("Elige tu jugada:", choices)

if st.button("Jugar"):
    comp_choice = random.choice(choices)
    st.write(f"Computadora eligió: {comp_choice}")

    if user_choice == comp_choice:
        st.success("¡Empate!")
    elif (user_choice == "Piedra" and comp_choice == "Tijera") or \
         (user_choice == "Papel" and comp_choice == "Piedra") or \
         (user_choice == "Tijera" and comp_choice == "Papel"):
        st.success("¡Ganaste! 🎉")
    else:
        st.error("Perdiste 😢")
