var Cookies = require('js-cookie');
var Parsley = require('parsleyjs');
var AWS = require('aws-sdk');
var AmazonCognitoIdentity = require('amazon-cognito-identity-js');
var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
var AWSCognito = require('aws-sdk/clients/cognitoidentity');


$(document).ready(function() {
  $('#signin-form').parsley();
  $('#login-form').parsley();
  $('#signin-form').submit(function(event){
    event.preventDefault();
    //AWSCognito.config.region = 'us-east-1';

    var formArray = $('#login-form').serializeArray();
    var userName = formArray[1].value;
    var password = formArray[2].value;

    var poolData = {
      UserPoolId: 'us-east-1_3Hlx0p8xs',
      ClientId: '7rttjsr0mhv2g3ci227kkf48t1'
    };

    var userPool = new CognitoUserPool(poolData);

    var attributeList = [];

    var dataEmail = {
      Name: 'email',
      Value: userName
    };

    var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);

    attributeList.push(attributeEmail);

    userPool.signUp(userName, password, attributeList, null, function(err, result) {
      if (err) {
        alert(err);
        return;
      }
      cognitoUser = result.user;
      console.log('user name is ' + cognitoUser.getUsername());
      var accessToken = result.getAccessToken().getJwtToken()
      Cookies.set('_auth_token', accessToken);

      $.ajax({
        url: $SCRIPT_ROOT + '/_get_user',
        type: 'POST',
        datatype: 'json',
        data: {accessToken: accessToken},
        //idToken: idToken},
        success: function(data) {
          console.log(data);
          Cookies.remove('_auth_token');
          window.location = data;},
        error: function() { alert('Failed!'); }
      });


    });
  });


  $("#login-form").submit(function(event) {
    event.preventDefault();
    var formArray = $('#login-form').serializeArray();
    console.log(formArray);
    console.log(formArray[1].value)
    console.log("clicked!");

    var userName = formArray[1].value;
    var password = formArray[2].value;

    AWS.config.region = 'us-east-1';
    var authenticationData = {
        Username : userName,//'hall2cm@yahoo.com',
        Password : password,//'0M@dison27',
    };
    var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
    var poolData = {
        UserPoolId : 'us-east-1_3Hlx0p8xs', // Your user pool id here
        ClientId : '7rttjsr0mhv2g3ci227kkf48t1' // Your client id here
    };
    var userPool = new CognitoUserPool(poolData);
    var userData = {
        Username : userName,//'hall2cm@yahoo.com',
        Pool : userPool
    };
    var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
            console.log("success");
            console.log('access token + ' + result.getAccessToken().getJwtToken());
            console.log('idToken + ' + result.idToken.jwtToken);
            var accessToken = result.getAccessToken().getJwtToken()
            var idToken = result.idToken.jwtToken
            Cookies.set('_auth_token', accessToken);
            Cookies.set('id_token', idToken);
            /*$.getJSON($SCRIPT_ROOT + '/_authenticate', {
              accessToken: result.getAccessToken().getJwtToken(),
              idToken: result.idToken.jwtToken
            }, function(data) {
              window.location = data;
            });*/

            $.ajax({
              url: $SCRIPT_ROOT + '/_authenticate',
              type: 'POST',
              datatype: 'json',
              //data: {accessToken: accessToken,
              //idToken: idToken},
              success: function(data) {
                console.log(data);
                window.location = data;},
              error: function() { alert('Failed!'); },
              //headers: { 'X-Auth-Token': accessToken}
            });
        },
        onFailure: function(err) {
            alert(err);
        }
    });



  });
  $(".logout").click(function() {
    console.log("logout");
    $.getJSON($SCRIPT_ROOT + '/_logout', {}, function(data) {
      console.log(data);
      var poolData = {
          UserPoolId : 'us-east-1_3Hlx0p8xs', // Your user pool id here
          ClientId : '7rttjsr0mhv2g3ci227kkf48t1' // Your client id here
      };
      var userPool = new CognitoUserPool(poolData);
      var userData = {
        Username: data,
        Pool: userPool
      };
      var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
      cognitoUser.signOut();
      Cookies.remove('_auth_token');
      Cookies.remove('id_token');
      window.location = $SCRIPT_ROOT + '/index'
    });
  });

});
