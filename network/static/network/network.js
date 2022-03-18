document.addEventListener('DOMContentLoaded', function() {
    
  document.getElementsByName('postlike').forEach(el => postlike(el.value)
    
  );

});


function likebutton(id) {
  // store request user
  const user_id = JSON.parse(document.getElementById('user_id').textContent);
  if (user_id){

  // get liked value and counter
  var el = document.getElementById(`postlike${id}`);
  var isliked = el.getAttribute('liked');
  var getcounter = el.innerHTML;
  var counterarray = getcounter.split(/(\s+)/)
  var counter = counterarray[2]

  
    if (isliked === "0") {
      counter++
      el.innerHTML = `&#10084; ` + counter;
      //update
      fetch(`/likes/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
        userid: user_id,
        postid: id,
        liked: 0, 
        })
      })
      el.setAttribute("liked", 1);
    } else {
      if (counter < 1){
        counter = 0
      } else {
        counter--
      }
      el.innerHTML = `&#129293; ` + counter;
      //delete
      fetch(`/likes/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
        userid: user_id,
        postid: id,
        liked: 1,
        })
      })
      el.setAttribute("liked", 0);
    }
  } else {
    alert("Login to like")
  }
}


function postlike(id) {
  //fetch selected email
  const user_id = JSON.parse(document.getElementById('user_id').textContent);

  fetch(`/likes/${id}`)
  .then(response => response.json())
  .then(like => { 
    var el = document.getElementById(`postlike${id}`)
    var counter = el.innerHTML
    if (!like.likeduser.length) {
      el.innerHTML = `&#129293; ` + counter;
      el.setAttribute("liked", 0);
    } else {
      for (i = 0; i < like.likeduser.length; ++i){
        if (like.likeduser[i].user === user_id){
          el.innerHTML = `&#10084; ` + counter;
          el.setAttribute("liked", 1);
          break
        } else {
          el.innerHTML = `&#129293; ` + counter;
          el.setAttribute("liked", 0);
        } 
      }
    }

  }); 
}

function editpost(id) {
  //fetch selected post
  fetch(`/edit/${id}`)
  .then(response => response.json())
  .then(post => {
  
      if (!post.error){
        if (document.getElementById(`cancelbutton${post.id}`)){
          document.getElementById(`editbutton${post.id}`).style.display = 'none';
          document.getElementById(`cancelbutton${post.id}`).style.display = 'block';
          document.getElementById(`savebutton${post.id}`).style.display = 'block';
          document.getElementById(`edittext${post.id}`).disabled = false;    
        }else{
          document.getElementById(`editbutton${post.id}`).style.display = 'none';
          document.getElementById(`edittext${post.id}`).disabled = false;
          divedit = document.getElementById(`edit${post.id}`)
          const cancelbutton = document.createElement('button');
          cancelbutton.id = `cancelbutton${post.id}`;
          cancelbutton.className="btn btn-danger";
          cancelbutton.innerHTML = 'Cancel';
          const savebutton = document.createElement('button');
          savebutton.id = `savebutton${post.id}`;
          savebutton.className="btn btn-success";
          savebutton.innerHTML = 'Save';
          divedit.appendChild(savebutton);
          divedit.appendChild(cancelbutton);
          savebutton.addEventListener('click', () => savepost(post.id));
          cancelbutton.addEventListener('click', () => cancelpost(post.id));
        }
      } else {
        alert(post.error)
      }

  });
  
}

function cancelpost(id) {
  fetch(`/edit/${id}`)
  .then(response => response.json())
  .then(post => {
    document.getElementById(`edittext${id}`).value = post.post;

  });
  document.getElementById(`cancelbutton${id}`).style.display = 'none';
  document.getElementById(`savebutton${id}`).style.display = 'none';
  document.getElementById(`editbutton${id}`).style.display = 'block';
  document.getElementById(`edittext${id}`).disabled = true;
}

function savepost(id) {
  var edittxt = document.getElementById(`edittext${id}`).value;
   fetch(`/edit/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
    post: edittxt    
    })
  })
 
  document.getElementById(`cancelbutton${id}`).style.display = 'none';
  document.getElementById(`savebutton${id}`).style.display = 'none';
  document.getElementById(`editbutton${id}`).style.display = 'block';
  document.getElementById(`edittext${id}`).disabled = true;
}

