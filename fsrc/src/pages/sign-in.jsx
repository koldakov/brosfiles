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
import store from '../store';

export default ({ f7router }) => {
  const url = `${URL_PREFIX}/auth/tokens/obtain/`;

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  let options = {};
  const signIn = () => {
    axios({
      method: 'post',
      url: url,
      data: {
        username: username,
        password: password,
      }
    }).then((response) => {
      store.dispatch("setAccessToken", response.data.access);
      store.dispatch("setRefreshToken", response.data.refresh);
      store.dispatch("setIsAuthenticated", true);
      f7router.navigate('/');
    }, (error) => {
      if (error.response.status === 401) {
        f7.dialog.alert('Username or password is incorrect!', "Oops!");
        return;
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
          onInput={(e) => {
            setUsername(e.target.value);
          }}
        />
        <ListInput
          name="password"
          label="Password"
          type="password"
          placeholder="Password"
          value={password}
          onInput={(e) => {
            setPassword(e.target.value);
          }}
        />
      </List>
      <List inset>
        <ListButton onClick={signIn}>Sign In</ListButton>
        <BlockFooter>
          <p>
            Don't have an account? <Link fill href="/sign-up/">Sign up!</Link>
          </p>
        </BlockFooter>
      </List>
    </Page>
  );
};
