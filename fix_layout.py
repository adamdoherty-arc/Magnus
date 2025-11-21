import time

file_path = 'src/ava/omnipresent_ava_enhanced.py'

# Read
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove icons
content = content.replace('"📊 Portfolio"', '"Portfolio"')
content = content.replace('"🎯 Opportunities"', '"Opportunities"')
content = content.replace('"📈 Watchlist"', '"Watchlist"')
content = content.replace('"❓ Help"', '"Help"')

# 2. Rename column
content = content.replace('img_col, actions_col = st.columns([1, 3])', 'img_col, content_col = st.columns([1, 3])')
content = content.replace('with actions_col:', 'with content_col:')

# 3. Move chat section inside content_col by adding indentation
# Find the section after last button
old_section = """                    st.rerun()

        # SECTION 1: Conversation History"""

new_section = """                    st.rerun()

            # SECTION 1: Conversation History"""

content = content.replace(old_section, new_section)

# Fix all subsequent lines in chat and input sections
old_chat_if = """            # SECTION 1: Conversation History - ONLY show if there are messages
        if st.session_state.ava_messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)

            # Display last 10 messages for better context
            for idx, msg in enumerate(st.session_state.ava_messages[-10:]):
                if msg['role'] == 'user':
                    st.markdown(f'<div class="user-message-bubble">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
                else:
                    # AVA response
                    response_text = msg['content']
                    confidence = msg.get('confidence', 0.8)
                    response_time = msg.get('response_time', 0.0)

                    st.markdown(f'<div class="ava-message-bubble">🤖 {response_text}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

                    # Meta info below message
                    meta_info = []
                    if response_time > 0:
                        time_emoji = "⚡" if response_time < 1.0 else ("⏱️" if response_time < 2.0 else "⚠️")
                        meta_info.append(f"{time_emoji} {response_time:.2f}s")

                    if confidence < 0.8:
                        conf_emoji = "💎" if confidence >= 0.9 else ("💡" if confidence >= 0.7 else "🤔")
                        meta_info.append(f"{conf_emoji} {confidence*100:.0f}% confident")

                    if meta_info:
                        st.caption(" | ".join(meta_info))

                    # Feedback buttons only for last message
                    if idx == len(st.session_state.ava_messages[-10:]) - 1:
                        feedback_col1, feedback_col2, feedback_spacer = st.columns([1, 1, 8])
                        with feedback_col1:
                            if st.button("👍", key=f"helpful_{len(st.session_state.ava_messages)}", help="Helpful", use_container_width=True):
                                st.session_state.enhanced_ava._log_feedback(len(st.session_state.ava_messages) - 1, 'positive')
                                st.toast("Thanks for the feedback!", icon="✅")
                        with feedback_col2:
                            if st.button("👎", key=f"not_helpful_{len(st.session_state.ava_messages)}", help="Not helpful", use_container_width=True):
                                st.session_state.enhanced_ava._log_feedback(len(st.session_state.ava_messages) - 1, 'negative')
                                st.toast("Thanks! I'll improve.", icon="📝")

            st.markdown('</div>', unsafe_allow_html=True)

        # SECTION 2: Input Area (Modern messenger style - integrated button)
        st.markdown('<div class="input-container">', unsafe_allow_html=True)

        # Use columns to integrate button into input visually
        input_col, button_col = st.columns([6, 1])

        with input_col:
            # Placeholder text based on conversation state
            placeholder = "Type your message..." if st.session_state.ava_state == ConversationState.IDLE else "Your answer..."

            user_input = st.text_input(
                "message_input",
                key="ava_input_enhanced",
                placeholder=placeholder,
                label_visibility="collapsed"
            )

        with button_col:
            send_button = st.button("Send", key="send_inline_btn", type="primary", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Process message if sent
        if send_button and user_input:
                # Add user message
                st.session_state.ava_messages.append({
                    'role': 'user',
                    'content': user_input
                })

                # Get AVA response
                ava = st.session_state.enhanced_ava
                response_data = ava.process_message(
                    user_input,
                    user_id=st.session_state.get('user_id', 'web_user'),
                    platform='web'
                )

                # Add AVA response with timing and confidence
                st.session_state.ava_messages.append({
                    'role': 'ava',
                    'content': response_data['response'],
                    'response_time': response_data.get('response_time', 0.0),
                    'confidence': response_data.get('confidence', 0.8)
                })

                # Rerun to show new messages
                st.rerun()"""

new_chat_if = """            # SECTION 1: Conversation History - ONLY show if there are messages
            if st.session_state.ava_messages:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)

                # Display last 10 messages for better context
                for idx, msg in enumerate(st.session_state.ava_messages[-10:]):
                    if msg['role'] == 'user':
                        st.markdown(f'<div class="user-message-bubble">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                        st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
                    else:
                        # AVA response
                        response_text = msg['content']
                        confidence = msg.get('confidence', 0.8)
                        response_time = msg.get('response_time', 0.0)

                        st.markdown(f'<div class="ava-message-bubble">🤖 {response_text}</div>', unsafe_allow_html=True)
                        st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

                        # Meta info below message
                        meta_info = []
                        if response_time > 0:
                            time_emoji = "⚡" if response_time < 1.0 else ("⏱️" if response_time < 2.0 else "⚠️")
                            meta_info.append(f"{time_emoji} {response_time:.2f}s")

                        if confidence < 0.8:
                            conf_emoji = "💎" if confidence >= 0.9 else ("💡" if confidence >= 0.7 else "🤔")
                            meta_info.append(f"{conf_emoji} {confidence*100:.0f}% confident")

                        if meta_info:
                            st.caption(" | ".join(meta_info))

                        # Feedback buttons only for last message
                        if idx == len(st.session_state.ava_messages[-10:]) - 1:
                            feedback_col1, feedback_col2, feedback_spacer = st.columns([1, 1, 8])
                            with feedback_col1:
                                if st.button("👍", key=f"helpful_{len(st.session_state.ava_messages)}", help="Helpful", use_container_width=True):
                                    st.session_state.enhanced_ava._log_feedback(len(st.session_state.ava_messages) - 1, 'positive')
                                    st.toast("Thanks for the feedback!", icon="✅")
                            with feedback_col2:
                                if st.button("👎", key=f"not_helpful_{len(st.session_state.ava_messages)}", help="Not helpful", use_container_width=True):
                                    st.session_state.enhanced_ava._log_feedback(len(st.session_state.ava_messages) - 1, 'negative')
                                    st.toast("Thanks! I'll improve.", icon="📝")

                st.markdown('</div>', unsafe_allow_html=True)

            # SECTION 2: Input Area (Modern messenger style - integrated button)
            st.markdown('<div class="input-container">', unsafe_allow_html=True)

            # Use columns to integrate button into input visually
            input_col, button_col = st.columns([6, 1])

            with input_col:
                # Placeholder text based on conversation state
                placeholder = "Type your message..." if st.session_state.ava_state == ConversationState.IDLE else "Your answer..."

                user_input = st.text_input(
                    "message_input",
                    key="ava_input_enhanced",
                    placeholder=placeholder,
                    label_visibility="collapsed"
                )

            with button_col:
                send_button = st.button("Send", key="send_inline_btn", type="primary", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Process message if sent
            if send_button and user_input:
                    # Add user message
                    st.session_state.ava_messages.append({
                        'role': 'user',
                        'content': user_input
                    })

                    # Get AVA response
                    ava = st.session_state.enhanced_ava
                    response_data = ava.process_message(
                        user_input,
                        user_id=st.session_state.get('user_id', 'web_user'),
                        platform='web'
                    )

                    # Add AVA response with timing and confidence
                    st.session_state.ava_messages.append({
                        'role': 'ava',
                        'content': response_data['response'],
                        'response_time': response_data.get('response_time', 0.0),
                        'confidence': response_data.get('confidence', 0.8)
                    })

                    # Rerun to show new messages
                    st.rerun()"""

content = content.replace(old_chat_if, new_chat_if)

# Write
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed layout!")
