import React, { useState } from 'react';
import {
  Page,
  LoginScreenTitle,
  List,
  ListInput,
  ListButton,
  BlockFooter,
  f7,
  Link,
} from 'framework7-react';
import axios from 'axios';
import { URL_PREFIX } from '../constants';

export default ({ f7router }) => {
  const url = `${URL_PREFIX}/auth/sign-up/`;

  const [username, setUsername] = useState('');
  const [usernameError, setUsernameError] = useState('');

  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  const [firstName, setFirstName] = useState('');
  const [firstNameError, setFirstNameError] = useState('');

  const [lastName, setLastName] = useState('');
  const [lastNameError, setLastNameError] = useState('');

  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');

  const signUp = () => {
    if (password1 !== password2) {
      f7.dialog.alert("<p>Passwords does not match!</p>", "Please fix the errors");
      setPassword2('');
      return;
    }
    axios({
      method: 'post',
      url: url,
      data: {
        username: username,
        email: email,
        first_name: firstName,
        last_name: lastName,
        password: password1,
      }
    }).then((response) => {
      if (response.data.user.is_active === true) {
        f7.dialog.alert('You can Sign In now!', 'Congratulations!');
        f7router.navigate('/sign-in/');
      }
    }, (error) => {
      if (error.response.status === 400) {
        if (error.response.data.message) {
          f7.dialog.alert(error.response.data.message, 'Oops!');
          return;
        }
        setUsernameError(error.response.data.username);
        setEmailError(error.response.data.email);
        setFirstNameError(error.response.data.first_name);
        setLastNameError(error.response.data.last_name);
      } else {
        f7.dialog.alert("<p>Refresh the page and try again!</p>", "Something went wrong!");
      }
    });
  };
  return (
    <Page noToolbar noNavbar noSwipeback loginScreen>
      <LoginScreenTitle>BrosFiles</LoginScreenTitle>
      <List form>
        <ListInput
          name="username"
          label="Username"
          type="text"
          placeholder="Username"
          value={username}
          autofocus
          errorMessage={usernameError}
          errorMessageForce
          onInput={(e) => {
            setUsername(e.target.value);
          }}
        />
        <ListInput
          name="email"
          label="Email"
          type="email"
          placeholder="Email"
          value={email}
          validate
          errorMessage={emailError}
          errorMessageForce
          onInput={(e) => {
            setEmail(e.target.value);
          }}
        />
        <ListInput
          name="first_name"
          label="First Name"
          type="text"
          placeholder="First Name"
          value={firstName}
          errorMessage={firstNameError}
          errorMessageForce
          onInput={(e) => {
            setFirstName(e.target.value);
          }}
        />
        <ListInput
          name="last_name"
          label="Last Name"
          type="text"
          placeholder="Last Name"
          value={lastName}
          errorMessage={lastNameError}
          errorMessageForce
          onInput={(e) => {
            setLastName(e.target.value);
          }}
        />
        <ListInput
          name="password1"
          label="Password"
          type="password"
          placeholder="Password"
          value={password1}
          onInput={(e) => {
            setPassword1(e.target.value);
          }}
        />
        <ListInput
          name="password2"
          label="Confirm password"
          type="password"
          placeholder="Confirm password"
          value={password2}
          onInput={(e) => {
            setPassword2(e.target.value);
          }}
        />
      </List>
      <List inset>
        <ListButton onClick={signUp}>Sign Up</ListButton>
        <BlockFooter>
          <p>
            Already have an account? <Link fill href="/sign-in/">Sign in!</Link>
          </p>
        </BlockFooter>
      </List>
    </Page>
  );
};
