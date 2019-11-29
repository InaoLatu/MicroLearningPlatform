
	function getMicroLearningContent(url){

		var request = new XMLHttpRequest();
		request.open("GET", url, false);
		request.send(null);

		if (request.status === 200) {
		  return JSON.parse(request.responseText);
		}

		//It is better to use asynchronous calls
	}

	function showMicroLearningContent(content){

		showTitle(content["title"]);
		showContent(content["text"], content["video"]);
		showQuiz(content["quiz"]);
	}

	function showTitle(title){
		var h1 = document.createElement("h1");
		h1.appendChild(document.createTextNode(title));
		document.getElementById("micro-learning").appendChild(h1);
	}

	function showContent(text, video){
		var h2 = document.createElement("h2");
		h2.appendChild(document.createTextNode("Content"));
		document.getElementById("micro-learning").appendChild(h2);

		var p = document.createElement("p");
		p.appendChild(document.createTextNode(text[0]));
		document.getElementById("micro-learning").appendChild(p);

		displayVideo(video["url"], video["format"]);

		p = document.createElement("p");
		p.appendChild(document.createTextNode(text[1]));
		document.getElementById("micro-learning").appendChild(p);
	}

	function displayVideo(url, format){
		var source = document.createElement("source");
		source.setAttribute("src", url);
		source.setAttribute("type", "video/"+format);

		var video = document.createElement("video");
		video.setAttribute("width", "320");
		video.setAttribute("height", "240");
		video.setAttribute("controls", "");

		video.appendChild(source);
		video.appendChild(document.createTextNode("Your browser does not support the video tag."));

		document.getElementById("micro-learning").appendChild(video);
	}

	function showQuiz(quiz){

		var h2 = document.createElement("h2");
		h2.appendChild(document.createTextNode("Quiz"));
		document.getElementById("micro-learning").appendChild(h2);

		var ol = document.createElement("ol");
		for(var i=0; i<quiz.length; i++){
			ol.appendChild(createQuestion(quiz[i], i));
		}

		document.getElementById("micro-learning").appendChild(ol);
	}

	function createQuestion(q, number){

		var group = document.createElement("li");

		var question = document.createElement("p");
		question.appendChild(document.createTextNode(q["question"]));

		group.appendChild(question);

		var choices = [];

		for(var i=0; i<q["choices"].length; i++){
			var input = document.createElement("input");
			input.setAttribute("type", "radio");
			input.setAttribute("name", "choice"+number);
			input.setAttribute("value", q["choices"][i]);

			var choice = document.createElement("div");
			choice.appendChild(input);
			choice.appendChild(document.createTextNode(q["choices"][i]))

			group.appendChild(choice);
		}

		var input = document.createElement("input");
		input.setAttribute("type", "hidden");
		input.setAttribute("value", q["answer"]);
		input.setAttribute("id", "answer"+number);

		var answer = document.createElement("div");
		answer.appendChild(input);
		group.appendChild(answer);

		var solution = document.createElement("p");
		solution.setAttribute("id", "solution"+number);
		group.appendChild(solution);


		var explanation = document.createElement("p");
		explanation.appendChild(document.createTextNode(q["explanation"]));
		explanation.setAttribute("id", "explanation"+number);
		explanation.setAttribute("hidden", "true");
		group.appendChild(explanation);

		return group;

	}

	function correctQuiz(){
		var questions = 5;
		var mark = 0;
		for(var i=0; i<questions; i++){
			mark += correctQuestion(i);
		}
		if(isNaN(mark)){
			document.getElementById("result").innerHTML = "You have to answer all the questions";
		}else{
			//document.getElementById("mark").value = mark;
			document.getElementById("result").innerHTML = "Your mark is: "+mark+"/"+questions;
			//document.getElementById("submit").removeAttribute("hidden");
		}
	}

	function correctQuestion(number){
		var choices = document.getElementsByName("choice"+number);
		var answer = document.getElementById("answer"+number).value;
		var solution = document.getElementById("solution"+number);
		for(var i=0; i<choices.length; i++){
			if(choices[i].checked){
				document.getElementById("explanation"+number).removeAttribute("hidden");
				if(choices[i].value == answer){
					solution.innerHTML = "Correct";
					return 1;
				}else{
					solution.innerHTML = "Incorrect";
					return 0;
				}
			}
		}
	}