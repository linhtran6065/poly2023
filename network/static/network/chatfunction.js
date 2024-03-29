// MESSAGE INPUT
const textarea = document.querySelector('.chatbox-message-input')
const chatboxForm = document.querySelector('.chatbox-message-form')

textarea.addEventListener('input', function () {
	let line = textarea.value.split('\n').length

	if (textarea.rows < 6 || line < 6) {
		textarea.rows = line
	}

	if (textarea.rows > 1) {
		chatboxForm.style.alignItems = 'flex-end'
	} else {
		chatboxForm.style.alignItems = 'center'
	}
})




// TOGGLE CHATBOX
const chatboxToggle = document.querySelector('.chatbox-toggle')
const chatboxMessage = document.querySelector('.chatbox-message-wrapper')

chatboxToggle.addEventListener('click', function () {
	chatboxMessage.classList.toggle('show')
})



// DROPDOWN TOGGLE
const dropdownToggle = document.querySelector('.chatbox-message-dropdown-toggle')
const dropdownMenu = document.querySelector('.chatbox-message-dropdown-menu')

dropdownToggle.addEventListener('click', function () {
	dropdownMenu.classList.toggle('show')
})

document.addEventListener('click', function (e) {
	if (!e.target.matches('.chatbox-message-dropdown, .chatbox-message-dropdown *')) {
		dropdownMenu.classList.remove('show')
	}
})







// CHATBOX MESSAGE
const chatboxMessageWrapper = document.querySelector('.chatbox-message-content')
const chatboxNoMessage = document.querySelector('.chatbox-message-no-message')

chatboxForm.addEventListener("keydown", function (e) {
	console.log("key down")
	if (!e) { var e = window.event; }
	//e.preventDefault(); // sometimes useful

	// Enter is pressed
	if (e.keyCode == 13) {
		if (isValid(textarea.value)) {
			console.log("message is " + textarea.value)
			setTimeout(autoReply(textarea.value), 1000)
			writeMessage()
		}

	}


});

chatboxForm.addEventListener('submit', function (e) {
	e.preventDefault()

	if (isValid(textarea.value)) {
		console.log("message is " + textarea.value)
		setTimeout(autoReply(textarea.value), 1000)
		writeMessage()
	}
})

// FIX CỨNG


function nhanNegative() {
	//turn on chat box message
	chatboxMessage.classList.toggle('show')
	const today = new Date()
	let message = `
	<div class="chatbox-message-item received">
		<span class="chatbox-message-item-text">
			Hello there, how was everything going? Do you need a person to talk with?
		</span>
		<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
	</div>
`
	chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
	scrollBottom()
}

function nhanPositive() {
	//turn on chat box message
	chatboxMessage.classList.toggle('show')
	const today = new Date()
	let message = `
	<div class="chatbox-message-item received">
		<span class="chatbox-message-item-text">
			We want to say thank you for your effort to spread positivity energy to the community:3
		</span>
		<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
	</div>
`
	chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
	scrollBottom()
}




function addZero(num) {
	return num < 10 ? '0' + num : num
}

function writeMessage() {
	const today = new Date()

	let message = `
		<div class="chatbox-message-item sent">
			<span class="chatbox-message-item-text">
				${textarea.value.trim().replace(/\n/g, '<br>\n')}
			</span>
			<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
		</div>
	`
	chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
	chatboxForm.style.alignItems = 'center'
	textarea.rows = 1
	textarea.focus()
	textarea.value = ''
	chatboxNoMessage.style.display = 'none'
	scrollBottom()
}



function autoReply(msg) {
	console.log("ULATRRRRRR " + msg)
	console.log("ULATRRRRRR " + msg)
	console.log("ULATRRRRRR " + msg)

	const today = new Date()

	const cautraloicuabot = fetch('/chatapi/' + msg,
		{
			method: 'POST',
		}
	)
		.then((response) => response.json())
		.then((cautraloicuabot) => {
			console.log("bot reply response " + cautraloicuabot["reply"])
			return cautraloicuabot;
		});

	const getAPI = () => {
		cautraloicuabot.then((a) => {
			console.log("bot reply " + a["reply"])
			let message = `
				<div class="chatbox-message-item received">
					<span class="chatbox-message-item-text">
					${a["reply"]}
					</span>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
			`
			chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
			scrollBottom()
			if (a["msg1"] != "") {
				let message = `
				<div class="chatbox-message-item received">
					<span class="chatbox-message-item-text">
					${a["msg1"]}
					</span>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()

				message = `
				<div class="chatbox-message-item received">
					<img src="${a["img_msg1"]}">
					</img>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()

				message = `
				<div class="chatbox-message-item received">
					<span class="chatbox-message-item-text">
					${a["msg2"]}
					</span>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()

				message = `
				<div class="chatbox-message-item received">
					<img src="${a["img_msg2"]}">
					</img>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()

				message = `
				<div class="chatbox-message-item received">
					<span class="chatbox-message-item-text">
					${a["msg3"]}
					</span>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()

				message = `
				<div class="chatbox-message-item received">
					<span class="chatbox-message-item-text">
						<a href = http://127.0.0.1:8000/n/quizz_mental target="_blank">Click here to do the test</a>
					</span>
					<span class="chatbox-message-item-time">${addZero(today.getHours())}:${addZero(today.getMinutes())}</span>
				</div>
				`
				chatboxMessageWrapper.insertAdjacentHTML('beforeend', message)
				scrollBottom()
			}
		});
	};

	getAPI();

}

function scrollBottom() {
	chatboxMessageWrapper.scrollTo(0, chatboxMessageWrapper.scrollHeight)
}

function isValid(value) {
	let text = value.replace(/\n/g, '')
	text = text.replace(/\s/g, '')

	return text.length > 0
}