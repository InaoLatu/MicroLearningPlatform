# Repository and Web authoring tool for micro learning content
Tech stack: Django, Python, MongoDB, Javascript, HTML and CSS.\
The aim of this project is to build a Repository and Web authoring
tool for micro learning content which allows the instructors to have an overall control over the
micro learning content they create. That includes all the stages from the registration of the
instructor in the platform to the creation and edition of every micro content of his own.

To accomplish the mission of this project they have been created several modules to build the whole archicture. These modules are the following:

- [Microlearning Telegram bot](https://github.com/InaoLatu/MicroLearningBot). Telegram Bot built to allow the students to consume the micro-content within the different Units.

- [AuthServer](https://github.com/InaoLatu/AuthServer). Tool to authenticate and authorize users to give them access to a third-party platform resources.

- [GeneralManager](https://github.com/InaoLatu/GeneralManager). Overall management system of the whole architecture.

- [StudentManager](https://github.com/InaoLatu/StudentManager). Server to manage the data and activity of the students. 

An example of the flow that will be followed when a Student wants to consume 1 micro content would be the following: 

![Flow of the different requests to get 1 micro-content](https://github.com/InaoLatu/MicroLearningPlatform/blob/tfg_inao/bot_requests_1_micro-content.png)

(It goes from the moment that the Student requests the micro content in the Telegram bot until it is presented to himself in the screen)
