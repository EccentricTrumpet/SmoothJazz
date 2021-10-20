import { Component } from '@angular/core';
import { NavigationStart, Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { CookieService } from 'ngx-cookie-service';
import { CreateGameRequest } from 'proto-gen/shengji_pb';
import { ShengjiClient } from 'proto-gen/ShengjiServiceClientPb';
import { environment } from 'src/environments/environment';
import { COOKIE_PLAYER_NAME, COOKIE_GAME_SPEED } from './app.constants';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styleUrls: ['app.component.scss'],
})
export class AppComponent {
  private client: ShengjiClient;

  constructor(
    private router: Router,
    private alertController: AlertController,
    private cookieService: CookieService) {
    // Close any opened dialog when route changes
    router.events.subscribe(async event => {
      if (event instanceof NavigationStart) {
        try { await this.alertController.dismiss(); } catch { }
      }
    });

    this.client = new ShengjiClient(environment.grpcUrl);
  }

  async createGame() {
    console.log('Creating new game');
    let playerName = this.cookieService.get(COOKIE_PLAYER_NAME);
    let gameSpeed = this.cookieService.get(COOKIE_GAME_SPEED);
    const alert = await this.alertController.create({
      header: 'Please Enter Your Name:',
      inputs: [
        {
          name: 'playerName',
          placeholder: '<Player Name>',
          value: playerName
        },
        {
          name: 'gameSpeed',
          placeholder: '10',
          value: gameSpeed
        },
        {
          name: 'debugMode',
          placeholder: 'False'
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
        },
        {
          text: 'Ok',
          handler: async inputData => {
            console.log(`Player name: ${inputData.playerName}`);
            playerName = inputData.playerName;
            gameSpeed = inputData.gameSpeed;
            debugMode = inputData.debugMode;
            this.cookieService.set(COOKIE_PLAYER_NAME, playerName);
            this.cookieService.set(COOKIE_GAME_SPEED, gameSpeed);

            let createGameRequest = new CreateGameRequest();
            createGameRequest.setPlayerName(playerName);
            createGameRequest.setGameSpeed(gameSpeed);
            createGameRequest.setShowOtherPlayerHands(debugMode);

            let response = await this.client.createGame(createGameRequest, null);
            this.router.navigate([`game/${response.getGameId()}`]);
          }
        }
      ]
    });
    await alert.present();
  }

  async joinGame() {
    console.log('Joining existing game!');
    let playerName = this.cookieService.get(COOKIE_PLAYER_NAME);
    const alert = await this.alertController.create({
      header: 'Please Enter Game Room ID and Your Name:',
      inputs: [
        {
          name: 'gameId',
          placeholder: '<Game Room ID>'
        },
        {
          name: 'playerName',
          placeholder: '<Player Name>',
          value: playerName
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
        },
        {
          text: 'Ok',
          handler: inputData => {
            console.log(`Player entered: ${JSON.stringify(inputData)}`);
            playerName = inputData.playerName;
            this.cookieService.set(COOKIE_PLAYER_NAME, playerName);
            this.router.navigate([`game/${inputData.gameId}`]);
          }
        }
      ]
    });
    await alert.present();
  }

  showAlert() {
    alert('Not yet implemented!');
  }
}
